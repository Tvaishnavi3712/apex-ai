"""
mentor_query — MentorAgent retrieval backbone. Takes a natural-language
question, scans the indexed Verizon KB documents, and returns the most
relevant passages with verbatim citations and confidence.

For the demo it uses simple lexical matching over the four runbook/KB
excerpts under `synthetic-data/verizon_far_edge/demo_docs/`. Production
would swap to Apex Lens / vector RAG without changing the contract.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.telecommunications._shared import DATA_ROOT  # noqa: E402

DOC_DIR = DATA_ROOT / "demo_docs"


# Tokens we treat as low-signal when scoring matches.
_STOP = {"a","an","and","the","or","of","to","is","are","was","what","why","how","when",
         "for","in","on","at","does","do","with","from","by","be","as","this","that",
         "tell","me","about","i","we","you","please","verizon","far","edge"}


def _tokens(s: str) -> List[str]:
    return [t for t in re.findall(r"[A-Za-z0-9_./\-]+", (s or "").lower()) if t not in _STOP and len(t) > 1]


def _score_passage(qtokens: List[str], passage: str) -> int:
    ptokens = set(_tokens(passage))
    return sum(1 for q in qtokens if q in ptokens)


def _split_passages(text: str) -> List[Tuple[str, str]]:
    """Split a doc into named passages by '─── headings ───' or 'KB-…' anchors."""
    blocks: List[Tuple[str, str]] = []
    current_name = "Preamble"
    buf: List[str] = []
    for line in text.splitlines():
        # Hyphen-delimited heading line
        if re.match(r"^[─\-]{30,}$", line):
            if buf:
                blocks.append((current_name, "\n".join(buf).strip()))
                buf = []
            continue
        # Section heading lines following the hyphen blocks
        m = re.match(r"^\s*([0-9]+\.[0-9.]*|KB-[0-9]+-[0-9]+)\s+(.{1,80})$", line)
        if m and not buf:
            current_name = f"{m.group(1)} {m.group(2)}".strip()
        buf.append(line)
    if buf:
        blocks.append((current_name, "\n".join(buf).strip()))
    return blocks


@apex_action(ApexActionSchema(
    name="mentor_query",
    description="MentorAgent — answer engineering questions from the indexed Verizon KB with verbatim citations.",
    category="knowledge_retrieval",
    industry="telecommunications",
    input_schema=ActionInputSchema(description="Mentor Q&A request")
        .add_string("question", "Natural-language question", required=True)
        .add_number("max_passages", "Max citations to return (default 3)", required=False),
    output_schema=ActionOutputSchema(description="Mentor answer envelope")
        .add_string("status", "ok | error")
        .add_string("answer", "Short structured answer with inline citations")
        .add_string("citations", "List of {document, section, passage, confidence}")
        .add_number("confidence", "Aggregate 0.0-1.0 confidence")
        .add_string("hitl_flag",  "Set if the question touches a production change"),
))
def mentor_query(question: str, max_passages: int = 3) -> Dict[str, Any]:
    if not question or not question.strip():
        return {"status": "error", "error_type": "bad_arguments",
                "message": "question is required"}

    qtokens = _tokens(question)
    if not qtokens:
        return {"status": "error", "error_type": "bad_arguments",
                "message": "question must contain searchable tokens"}

    # Load all indexed docs
    if not DOC_DIR.is_dir():
        return {"status": "error", "error_type": "missing_data",
                "message": f"Demo doc folder missing: {DOC_DIR}"}

    candidates: List[Dict[str, Any]] = []
    for doc_path in sorted(DOC_DIR.glob("*.txt")):
        text = doc_path.read_text(encoding="utf-8", errors="ignore")
        for section_name, passage in _split_passages(text):
            score = _score_passage(qtokens, passage)
            if score == 0:
                continue
            candidates.append({
                "document":   doc_path.name,
                "section":    section_name,
                "passage":    passage[:600] + ("..." if len(passage) > 600 else ""),
                "score":      score,
            })

    candidates.sort(key=lambda c: -c["score"])
    top = candidates[:max(1, min(max_passages, 5))]
    if not top:
        return {
            "status":     "ok",
            "answer":     ("I could not find a matching passage in the indexed Verizon "
                           "Far Edge knowledge base. Recommend escalating to the cert-team-lead "
                           "or the vendor support engineer for this domain."),
            "citations":  [],
            "confidence": 0.0,
            "hitl_flag":  None,
        }

    confidence = round(min(1.0, top[0]["score"] / max(3, len(qtokens))), 2)
    citations = []
    for c in top:
        citations.append({
            "document":   c["document"],
            "section":    c["section"],
            "passage":    c["passage"],
            "confidence": round(c["score"] / max(1, len(qtokens)), 2),
        })

    # Heuristic answer = top passage, with safety flag for production-changing questions
    production_change_keywords = ("upgrade", "deploy", "rollback", "restart", "reboot",
                                  "change", "patch", "remediate", "rollback")
    hitl_flag = ("This answer touches a production change. Have a senior engineer review "
                 "before executing.") if any(k in question.lower() for k in production_change_keywords) else None

    return {
        "status":      "ok",
        "answer":      top[0]["passage"],
        "citations":   citations,
        "confidence":  confidence,
        "hitl_flag":   hitl_flag,
        "documents_searched": sorted(p.name for p in DOC_DIR.glob("*.txt")),
    }
