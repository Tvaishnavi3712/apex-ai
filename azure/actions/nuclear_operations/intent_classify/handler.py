"""
intent_classify — classify a free-text user query into one of ChatSTP's 4 intents.

Powers the ChatSTP router agent. Pure regex + keyword scoring (no LLM call
needed for routing — fast, deterministic, cheap). Also extracts canonical
entities (equipment_ids, doc numbers, time ranges) so downstream agents
don't have to re-parse the prompt.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402

# ---------------------------------------------------------------------------
# Intent definitions — keyword sets are weighted; max class wins.
# ---------------------------------------------------------------------------
_INTENT_KEYWORDS: Dict[str, Dict[str, float]] = {
    "policy_lookup": {
        "policy": 3, "allowance": 3, "per-diem": 3, "per diem": 3,
        "meal": 2, "travel": 2, "reimburse": 2, "overtime": 2, "pto": 2,
        "badge": 2, "vendor": 2, "training": 1.5,
        "stp-": 4, "section": 1, "tech spec": 4, "technical specification": 4,
        "what is": 1, "explain": 1,
    },
    "maintenance_history": {
        "last pm": 4, "previous pm": 4, "history": 3, "when was": 3,
        "who worked": 4, "who performed": 4, "who maintained": 4,
        "wo-": 4, "work order": 3, "work package": 3,
        "engineer": 2, "technician": 2,
    },
    "issue_analysis": {
        "common issues": 4, "common problems": 4, "failure": 3,
        "frequent": 2, "patterns": 2, "trend": 2,
        "what's wrong": 3, "what is wrong": 3, "history of failures": 4,
        "root cause": 3, "diagnose": 3,
    },
    "predictive_maintenance": {
        "predict": 4, "forecast": 3, "rul": 4, "remaining useful life": 4,
        "anomaly": 4, "risk score": 4, "recommend pm": 4,
        "next 30 days": 2, "will fail": 4, "going to fail": 4,
        "should i": 1, "advance pm": 3, "early warning": 3,
    },
}

# Equipment ID patterns: P-3A, EDG-2, MOV-7B, HX-22A, V-104, etc.
_EQ_RE = re.compile(r"\b([A-Z]{1,4}-\d{1,4}[A-Z]?)\b")
# Doc number: STP-415, STP-OP-2204, 0PMP-RCS-7B
_DOC_RE = re.compile(r"\b(STP-[A-Z]*-?\d+(?:\.\d+)?|0P[OM]P-[A-Z]+-?\w+)\b", re.IGNORECASE)
# Tech spec: TS 3.4.5
_TS_RE = re.compile(r"\b(?:tech\s*spec\s*|TS\s*)(\d+(?:\.\d+){1,2})\b", re.IGNORECASE)

# Friendly-name → canonical-id mapping. Engineers type "Pump-3A" / "Pump 3A"
# when they mean P-3A; same for valves, motors, EDGs, MOVs, HX. Map them so
# the downstream action handlers (which key off canonical ids like P-3A,
# MOV-7B, EDG-2) just work without per-handler logic.
_FRIENDLY_PREFIX_MAP = {
    "pump":          "P",
    "valve":         "V",
    "motor":         "M",
    "edg":           "EDG",
    "diesel":        "EDG",
    "generator":     "EDG",
    "mov":           "MOV",
    "hx":            "HX",
    "heatexchanger": "HX",
    "heat-exchanger": "HX",
    "hex":           "HX",
}
_FRIENDLY_RE = re.compile(
    r"\b(pump|valve|motor|edg|diesel(?:\s+generator)?|mov|hx|heat[-\s]?exchanger|hex)"
    r"[\s\-]+(\d{1,4}[a-zA-Z]?)\b",
    re.IGNORECASE,
)


def _score_intents(q: str) -> Dict[str, float]:
    """Tally weighted hits per intent."""
    qlower = q.lower()
    scores: Dict[str, float] = {}
    for intent, kw_map in _INTENT_KEYWORDS.items():
        s = 0.0
        for kw, weight in kw_map.items():
            if kw in qlower:
                s += weight * qlower.count(kw)
        scores[intent] = s
    return scores


def _extract_entities(q: str) -> Dict[str, List[str]]:
    """Extract equipment IDs (canonical + friendly), doc numbers, tech-spec citations."""
    eqs = set(_EQ_RE.findall(q))
    # Canonicalize friendly names: "Pump-3A" / "Pump 3A" → "P-3A"
    for friendly, suffix in _FRIENDLY_RE.findall(q):
        prefix = _FRIENDLY_PREFIX_MAP.get(friendly.lower().replace(" ", ""))
        if prefix:
            eqs.add(f"{prefix}-{suffix.upper()}")
    docs = sorted(set(m.upper() for m in _DOC_RE.findall(q)))
    ts_matches = sorted(set(_TS_RE.findall(q)))
    return {
        "equipment_ids": sorted(eqs),
        "doc_numbers": docs,
        "tech_specs": ts_matches,
    }


@apex_action(ApexActionSchema(
    name="intent_classify",
    description="Classify a user query into ChatSTP intent (policy_lookup, maintenance_history, issue_analysis, predictive_maintenance, unknown) and extract entities.",
    category="routing",
    industry="nuclear_operations",
    input_schema=ActionInputSchema(description="Intent classification request")
        .add_string("query", "Free-text user query", required=True),
    output_schema=ActionOutputSchema(description="Intent classification envelope")
        .add_string("status", "ok | error")
        .add_string("intent", "policy_lookup | maintenance_history | issue_analysis | predictive_maintenance | unknown")
        .add_number("confidence", "0..1")
        .add_string("entities_extracted", "Dict {equipment_ids, doc_numbers, tech_specs}")
        .add_string("intent_scores", "Raw per-intent score for debugging"),
))
def intent_classify(query: str) -> dict:
    """Classify `query` into one of 4 ChatSTP intents (or 'unknown' if all scores are 0)."""
    if not query or not query.strip():
        return {"status": "error", "error_type": "bad_arguments", "message": "query is required"}

    scores = _score_intents(query)
    entities = _extract_entities(query)

    # Boost intent based on extracted entities
    if entities["equipment_ids"]:
        scores["maintenance_history"] = scores.get("maintenance_history", 0) + 1
        scores["issue_analysis"] = scores.get("issue_analysis", 0) + 1
        scores["predictive_maintenance"] = scores.get("predictive_maintenance", 0) + 1
    if entities["doc_numbers"] or entities["tech_specs"]:
        scores["policy_lookup"] = scores.get("policy_lookup", 0) + 4

    best_intent = max(scores, key=scores.get) if scores else "unknown"
    best_score = scores.get(best_intent, 0)

    # If nothing scored, mark unknown
    if best_score <= 0:
        return {
            "status": "ok",
            "intent": "unknown",
            "confidence": 0.0,
            "entities_extracted": entities,
            "intent_scores": scores,
        }

    # Normalize confidence as best/total
    total = sum(scores.values())
    confidence = round(best_score / max(1.0, total), 3)

    return {
        "status": "ok",
        "intent": best_intent,
        "confidence": confidence,
        "entities_extracted": entities,
        "intent_scores": {k: round(v, 2) for k, v in scores.items()},
    }


def handler(event, context=None):
    return intent_classify(query=event.get("query", ""))
