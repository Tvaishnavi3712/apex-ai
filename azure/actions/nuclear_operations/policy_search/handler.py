"""
policy_search — keyword search across the STP policy & procedure corpus.

Reads `synthetic-data/nuclear_operations/policies_corpus.json` (a list of
hand-tuned policy/procedure docs that mirror what the PolicyAgent uses for
its in-process fallback). Returns the top-k matching sections with a simple
TF-IDF / token-overlap relevance score.

This handler is deliberately deterministic — same query → same ranking,
every time — so the demo is rehearsable.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

# Make the actions/ package importable when running standalone (Lambda layout
# normally takes care of this; for local pytest we walk up to aws/actions/).
sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.nuclear_operations._shared import (  # noqa: E402
    data_path, missing_data_envelope,
)
import json


def _load_policy_corpus() -> List[Dict[str, Any]]:
    """Read policies_corpus.json. Returns [] if missing — handler reports error."""
    path = data_path("policies_corpus.json")
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def _tokenize(s: str) -> List[str]:
    """Lowercase + word-boundary split + drop short stopwords."""
    stop = {"the", "a", "an", "of", "for", "to", "in", "on", "is", "and", "or", "what", "when",
            "how", "do", "i", "my", "our", "by", "be", "as", "at", "this", "that"}
    tokens = re.findall(r"[a-z0-9_$\.\-]+", s.lower())
    return [t for t in tokens if t and t not in stop and len(t) >= 2]


def _score_section(query_tokens: List[str], section: Dict[str, Any], doc: Dict[str, Any]) -> float:
    """Token overlap weighted by section heading + body + keywords."""
    body = section.get("text", "")
    heading = section.get("heading", "")
    keywords = " ".join(doc.get("keywords", []))
    haystack = f"{heading} {body} {keywords}".lower()
    if not haystack.strip():
        return 0.0
    score = 0.0
    for t in query_tokens:
        if t in haystack:
            # Heading hit weighs more, keyword hit weighs more, body once per occurrence
            score += haystack.count(t)
            if t in heading.lower():
                score += 3.0
            if t in keywords.lower():
                score += 2.0
    # Normalize roughly by haystack length so longer sections don't dominate
    score /= max(1.0, len(haystack) ** 0.5 / 4)
    return round(score, 4)


@apex_action(ApexActionSchema(
    name="policy_search",
    description="Search the STP policy & procedure corpus for the most relevant section(s) given a natural-language query.",
    category="business_logic",
    industry="nuclear_operations",
    input_schema=ActionInputSchema(description="Policy search request")
        .add_string("query", "Natural language query, e.g. 'max meal allowance for site travel'", required=True)
        .add_number("top_k", "Maximum number of results to return", required=False),
    output_schema=ActionOutputSchema(description="Ranked list of matching policy sections")
        .add_string("status", "ok | error")
        .add_string("results", "List of {doc_id, doc_number, title, section, heading, snippet, relevance_score}")
        .add_string("query_classification", "policy | procedure | tech_spec"),
))
def policy_search(query: str, top_k: int = 3) -> dict:
    """Search the policy corpus and return top-k matching sections."""
    if not query or not query.strip():
        return {"status": "error", "error_type": "bad_arguments", "message": "query is required"}

    corpus = _load_policy_corpus()
    if not corpus:
        return missing_data_envelope("policies_corpus.json")

    tokens = _tokenize(query)
    scored: List[Dict[str, Any]] = []
    for doc in corpus:
        for sec in doc.get("sections", []):
            score = _score_section(tokens, sec, doc)
            if score <= 0:
                continue
            text = sec.get("text", "")
            scored.append({
                "doc_id": doc.get("doc_id"),
                "doc_number": doc.get("doc_number"),
                "title": doc.get("title"),
                "section": sec.get("section"),
                "heading": sec.get("heading"),
                "snippet": text[:240] + ("…" if len(text) > 240 else ""),
                "verbatim_text": text,
                "effective_date": doc.get("effective_date"),
                "relevance_score": score,
            })
    scored.sort(key=lambda r: r["relevance_score"], reverse=True)

    # Classify intent for the router
    qlower = query.lower()
    if "tech spec" in qlower or "ts " in qlower or "limiting condition" in qlower:
        qcls = "tech_spec"
    elif "procedure" in qlower or "0pop" in qlower or "0pmp" in qlower:
        qcls = "procedure"
    else:
        qcls = "policy"

    return {
        "status": "ok",
        "results": scored[: max(1, int(top_k or 3))],
        "query_classification": qcls,
        "total_matches": len(scored),
    }


def handler(event, context=None):
    """Lambda entrypoint."""
    query = event.get("query", "")
    top_k = int(event.get("top_k", 3))
    return policy_search(query=query, top_k=top_k)
