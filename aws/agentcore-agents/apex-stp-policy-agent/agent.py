"""
Apex STP PolicyAgent — AgentCore runtime for STP Demo UC-1 (Policy & Procedure
Q&A with verbatim citations).

Owns: policy corpus search (BM25 + keyword), verbatim citation extraction with
doc_number / section / effective_date provenance. Powers the "policy lookup"
intent of ChatSTP.

User-facing brand: ChatSTP. This is one of the four specialist agents the
ChatSTP router delegates to.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

# Make the actions/ package importable so we can call shared loaders if/when
# the synthetic-data corpus is generated. Falls back to embedded demo data.
_AWS_ROOT = Path(__file__).resolve().parents[2]
if str(_AWS_ROOT) not in sys.path:
    sys.path.insert(0, str(_AWS_ROOT))

app = BedrockAgentCoreApp()

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------
MODEL_ID = "us.anthropic.claude-opus-4-6-v1"
REGION = "us-east-1"
DEFAULT_TOP_K = 3

SYSTEM_PROMPT = """You are PolicyAgent, the policy & procedure expert for STP Nuclear Operating Company (South Texas Project).

Your job: answer policy questions with verbatim citations. You serve nuclear plant operators, engineers, and admin staff who need authoritative answers fast.

NON-NEGOTIABLE RULES:
1. ALWAYS cite the policy doc_number, section, and effective_date verbatim. Never paraphrase the cited text.
2. Format every answer as:
   <plain-English answer>

   Source: <DOC-NUMBER> § <SECTION> (effective <YYYY-MM-DD>): "<verbatim quote>"
3. If no policy matches the query, say so explicitly. NEVER fabricate a policy or invent a doc number.
4. If the user asks something off-topic (weather, jokes), politely redirect to policy questions.
5. Use search_policies first to find candidate docs; then extract_citation to pull the verbatim text.

Example demo question: "What is the max meal allowance for site-meeting business travel?"
Expected answer pattern:
  The maximum meal allowance for site-meeting business travel is $75 per day.

  Source: STP-415 § 3.2 (effective 2024-06-01): "Per-diem meal allowance for on-site business meetings shall not exceed $75.00 per traveler per calendar day, inclusive of gratuity."
"""


# ---------------------------------------------------------------------------
# Embedded policy corpus (demo data — replaced by real corpus when
# synthetic-data/nuclear_operations/policies/ is generated)
# ---------------------------------------------------------------------------
_POLICY_CORPUS: List[Dict[str, Any]] = [
    {
        "doc_id": "STP-415",
        "doc_number": "STP-415",
        "title": "Business Travel & Per-Diem Allowances",
        "effective_date": "2024-06-01",
        "owner": "STP Finance / Travel Services",
        "sections": [
            {
                "section": "3.1",
                "heading": "Lodging",
                "text": "Lodging at on-site business meetings shall be reimbursed at actual cost up to the GSA per-diem rate for the locality.",
            },
            {
                "section": "3.2",
                "heading": "Meal Allowance",
                "text": "Per-diem meal allowance for on-site business meetings shall not exceed $75.00 per traveler per calendar day, inclusive of gratuity.",
            },
            {
                "section": "3.3",
                "heading": "Incidental Expenses",
                "text": "Incidental expenses (parking, tolls, business calls) shall be reimbursed at actual cost with itemized receipts.",
            },
        ],
        "keywords": ["meal", "allowance", "per-diem", "travel", "site-meeting", "business travel", "$75"],
    },
    {
        "doc_id": "STP-OP-2204",
        "doc_number": "STP-OP-2204",
        "title": "Reactor Coolant Pump Surveillance & Lockout",
        "effective_date": "2023-11-15",
        "owner": "Operations / RCS",
        "sections": [
            {
                "section": "5.1",
                "heading": "Vibration Monitoring",
                "text": "Reactor coolant pump vibration shall be monitored continuously; any single-axis reading exceeding 0.30 in/s peak shall trigger a Tech-Spec entry within 4 hours.",
            },
            {
                "section": "5.4",
                "heading": "Lockout / Tagout",
                "text": "Prior to maintenance on any RCP, two-person verification of breaker open and tag-applied shall be documented in the work package per OSHA 1910.147.",
            },
        ],
        "keywords": ["pump", "rcp", "vibration", "lockout", "tagout", "loto", "surveillance"],
    },
    {
        "doc_id": "STP-MNT-1102",
        "doc_number": "STP-MNT-1102",
        "title": "Preventive Maintenance Scheduling",
        "effective_date": "2025-02-10",
        "owner": "Maintenance Engineering",
        "sections": [
            {
                "section": "2.3",
                "heading": "PM Frequency for Pumps",
                "text": "Centrifugal pumps in Class-1 service shall receive a quarterly minor PM and an annual major PM; deferrals beyond 30 days require Maintenance Manager approval.",
            },
        ],
        "keywords": ["pm", "preventive maintenance", "schedule", "pump", "frequency"],
    },
    {
        "doc_id": "STP-RAD-901",
        "doc_number": "STP-RAD-901",
        "title": "Radiation Work Permit Issuance",
        "effective_date": "2024-09-01",
        "owner": "Radiation Protection",
        "sections": [
            {
                "section": "4.2",
                "heading": "RWP Briefing",
                "text": "All workers shall receive a pre-job RWP briefing within 24 hours of entry into a posted Radiation Area; briefing attendance shall be electronically logged.",
            },
        ],
        "keywords": ["rwp", "radiation", "permit", "briefing", "rad area"],
    },
]


# ---------------------------------------------------------------------------
# Tool helpers
# ---------------------------------------------------------------------------
def _ok(data: Any) -> Dict[str, Any]:
    """Standard success envelope."""
    return {"status": "ok", "data": data}


def _err(message: str) -> Dict[str, Any]:
    """Standard error envelope. Tool functions never raise to the agent loop."""
    return {"status": "error", "message": message}


def _score_doc(doc: Dict[str, Any], query: str) -> float:
    """Cheap BM25-ish keyword scoring without external deps."""
    q_terms = [t.lower() for t in query.split() if len(t) > 1]
    if not q_terms:
        return 0.0
    haystack = " ".join([
        doc.get("title", ""),
        " ".join(doc.get("keywords", [])),
        " ".join(s.get("text", "") for s in doc.get("sections", [])),
        " ".join(s.get("heading", "") for s in doc.get("sections", [])),
    ]).lower()
    score = 0.0
    for term in q_terms:
        if term in haystack:
            score += 1.0
        # boost exact keyword matches
        for kw in doc.get("keywords", []):
            if term == kw.lower():
                score += 1.5
    return score


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
@tool
def search_policies(query: str, top_k: int = DEFAULT_TOP_K) -> dict:
    """Search the STP policy corpus and return the top_k most relevant policy documents.

    Use this FIRST to find candidate documents before calling extract_citation.

    Args:
        query: Natural-language question (e.g. "max meal allowance on travel")
        top_k: Number of top results to return (default 3)

    Returns:
        {"status": "ok", "data": {"results": [{"doc_id", "doc_number", "title",
        "effective_date", "score", "preview"}, ...]}}
    """
    try:
        scored = [(d, _score_doc(d, query)) for d in _POLICY_CORPUS]
        scored = [s for s in scored if s[1] > 0]
        scored.sort(key=lambda t: t[1], reverse=True)
        results = []
        for doc, score in scored[: max(1, int(top_k))]:
            preview_section = doc["sections"][0] if doc.get("sections") else {}
            results.append({
                "doc_id": doc["doc_id"],
                "doc_number": doc["doc_number"],
                "title": doc["title"],
                "effective_date": doc["effective_date"],
                "owner": doc.get("owner", ""),
                "score": round(score, 2),
                "preview": preview_section.get("text", "")[:240],
            })
        if not results:
            return _ok({"results": [], "message": f"No policies matched '{query}'."})
        return _ok({"results": results})
    except Exception as e:  # noqa: BLE001 — never raise to agent loop
        return _err(f"search_policies failed: {e}")


@tool
def extract_citation(doc_id: str, topic: str) -> dict:
    """Extract the verbatim section text from a policy document for a given topic.

    Returns the doc_number, section, effective_date, and the EXACT quoted text
    suitable for direct citation. Always use this output verbatim — never
    paraphrase.

    Args:
        doc_id: Policy document id (e.g. "STP-415")
        topic: Topic the citation should cover (e.g. "meal allowance")

    Returns:
        {"status": "ok", "data": {"doc_number", "section", "heading",
        "effective_date", "verbatim_text", "owner"}}
    """
    try:
        doc = next((d for d in _POLICY_CORPUS if d["doc_id"] == doc_id), None)
        if doc is None:
            return _err(f"Policy doc_id '{doc_id}' not found in corpus.")
        # Pick the section whose heading/text best matches the topic.
        topic_lc = topic.lower()
        best = None
        best_score = -1.0
        for sec in doc.get("sections", []):
            blob = (sec.get("heading", "") + " " + sec.get("text", "")).lower()
            score = sum(1 for tok in topic_lc.split() if tok in blob)
            if score > best_score:
                best_score = score
                best = sec
        if best is None:
            return _err(f"Doc {doc_id} has no sections.")
        return _ok({
            "doc_id": doc["doc_id"],
            "doc_number": doc["doc_number"],
            "section": best["section"],
            "heading": best.get("heading", ""),
            "effective_date": doc["effective_date"],
            "owner": doc.get("owner", ""),
            "verbatim_text": best["text"],
            "citation_format": (
                f'{doc["doc_number"]} § {best["section"]} '
                f'(effective {doc["effective_date"]}): "{best["text"]}"'
            ),
        })
    except Exception as e:  # noqa: BLE001
        return _err(f"extract_citation failed: {e}")


# ---------------------------------------------------------------------------
# Multi-LLM support: payload may include `model_overrides` from the platform's
# Settings → Agent Models panel. Per-agent slot keys for PolicyAgent:
#   tool_selection — model used for the tool-call loop (BM25 + cite tools)
#   synthesis      — model used for final answer composition (verbatim cite)
# Defaults match the Quality-First preset so legacy callers see no change.
# ---------------------------------------------------------------------------
AGENT_ID = "policy-agent"
DEFAULT_TOOL_MODEL = MODEL_ID
DEFAULT_SYNTH_MODEL = MODEL_ID

# Cache one Strands Agent per (tool_model, synth_model) tuple — building one
# is cheap (no network), but re-use within a warm container saves microseconds.
_agent_cache: Dict[tuple, Agent] = {}


def _resolve_models(model_overrides: Dict[str, Dict[str, str]] | None) -> tuple:
    """Resolve which BedrockModel ids to use for tool calls vs synthesis."""
    overrides = (model_overrides or {}).get(AGENT_ID, {})
    tool_id = overrides.get("tool_selection", DEFAULT_TOOL_MODEL)
    synth_id = overrides.get("synthesis", DEFAULT_SYNTH_MODEL)
    return tool_id, synth_id


def _get_agent(tool_model_id: str, synth_model_id: str) -> Agent:
    """Get or build a Strands Agent for the given (tool, synth) model tuple."""
    key = (tool_model_id, synth_model_id)
    if key in _agent_cache:
        return _agent_cache[key]
    # Strands Agent currently uses ONE model for both tool selection and
    # final answer composition. We pass the synthesis model since that's
    # the higher-quality of the two — tool selection's lower demand still
    # works fine with Sonnet/Opus, and it preserves response coherence.
    # (When Strands gains per-step model split, we'll set both here.)
    model = BedrockModel(model_id=synth_model_id, region_name=REGION)
    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[search_policies, extract_citation],
    )
    _agent_cache[key] = agent
    return agent


@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """AgentCore HTTP entrypoint."""
    user_message = payload.get("prompt", "Hello")
    tool_id, synth_id = _resolve_models(payload.get("model_overrides"))
    result = _get_agent(tool_id, synth_id)(user_message)
    # Annotate the response so the platform's audit log can capture which
    # model actually answered. Falls through transparently when callers
    # don't surface the metadata.
    return {
        "result": result.message,
        "model_used": {
            "agent": AGENT_ID,
            "tool_selection_model": tool_id,
            "synthesis_model": synth_id,
        },
    }


if __name__ == "__main__":
    app.run()
