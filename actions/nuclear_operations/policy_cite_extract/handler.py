"""
policy_cite_extract — pull a verbatim policy citation by doc_id + topic.

Used by PolicyAgent when it has narrowed down to a specific document but
needs to surface the exact section text. Returns the document header block
(doc_number, revision, effective_date, owner) plus the matched section's
verbatim text — that header block is what the demo audience sees as the
"source" line under each answer.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.nuclear_operations._shared import (  # noqa: E402
    data_path, missing_data_envelope, not_found_envelope,
)


def _load_corpus() -> List[Dict[str, Any]]:
    path = data_path("policies_corpus.json")
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def _topic_match(section: Dict[str, Any], topic: str) -> int:
    """Score a section's relevance to a topic (heading + body + keyword overlap)."""
    if not topic:
        return 1
    haystack = f"{section.get('heading', '')} {section.get('text', '')}".lower()
    score = 0
    for word in re.findall(r"[a-z0-9$\.]+", topic.lower()):
        if len(word) < 3:
            continue
        if word in haystack:
            score += 1
    return score


@apex_action(ApexActionSchema(
    name="policy_cite_extract",
    description="Return the verbatim text of a policy section plus full document header for use in a citation.",
    category="business_logic",
    industry="nuclear_operations",
    input_schema=ActionInputSchema(description="Citation extraction request")
        .add_string("doc_id", "Policy document id, e.g. STP-415", required=True)
        .add_string("topic", "Topic to locate within the doc (optional — defaults to first section)", required=False),
    output_schema=ActionOutputSchema(description="Citation envelope")
        .add_string("status", "ok | error | not_found")
        .add_string("doc_number", "Doc number, e.g. STP-415")
        .add_string("section", "Section number, e.g. 3.2")
        .add_string("heading", "Section heading text")
        .add_string("verbatim_text", "Exact body text — caller should NOT paraphrase")
        .add_string("effective_date", "Doc effective date, ISO-8601")
        .add_string("owner", "Doc owner department/role")
        .add_string("revision", "Doc revision identifier")
        .add_string("citation_string", "Pre-formatted, e.g. 'STP-415 § 3.2 (effective 2024-06-01)'"),
))
def policy_cite_extract(doc_id: str, topic: str = "") -> dict:
    """Find the most relevant section in `doc_id` matching `topic` and return verbatim text."""
    if not doc_id:
        return {"status": "error", "error_type": "bad_arguments", "message": "doc_id is required"}

    corpus = _load_corpus()
    if not corpus:
        return missing_data_envelope("policies_corpus.json")

    doc: Optional[Dict[str, Any]] = next(
        (d for d in corpus if d.get("doc_id") == doc_id or d.get("doc_number") == doc_id), None,
    )
    if doc is None:
        return not_found_envelope("policy_doc", doc_id)

    sections = doc.get("sections", [])
    if not sections:
        return not_found_envelope("policy_section", f"{doc_id}/<any>")

    scored = sorted(
        ((sec, _topic_match(sec, topic or "")) for sec in sections),
        key=lambda x: x[1],
        reverse=True,
    )
    best, best_score = scored[0]
    # If topic was supplied but nothing matched, return first section but flag low confidence.
    confidence = "high" if best_score > 0 or not topic else "low"

    citation = (
        f"{doc.get('doc_number')} § {best.get('section')} "
        f"(effective {doc.get('effective_date')})"
    )

    return {
        "status": "ok",
        "doc_id": doc.get("doc_id"),
        "doc_number": doc.get("doc_number"),
        "title": doc.get("title"),
        "section": best.get("section"),
        "heading": best.get("heading"),
        "verbatim_text": best.get("text"),
        "effective_date": doc.get("effective_date"),
        "owner": doc.get("owner"),
        "revision": doc.get("revision"),
        "nrc_classification": doc.get("nrc_classification"),
        "citation_string": citation,
        "match_confidence": confidence,
    }


def handler(event, context=None):
    return policy_cite_extract(
        doc_id=event.get("doc_id", ""),
        topic=event.get("topic", ""),
    )
