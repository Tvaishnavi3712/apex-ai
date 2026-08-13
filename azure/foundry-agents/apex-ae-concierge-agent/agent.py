"""
Apex Agentic Enterprise — ConciergeAgent (UC-2, vendor-neutral demo).

Stateful conversational agent for Coral Star Cruises. Combines RAG over the
guest-services FAQ corpus with booking modification + sentiment monitoring +
seamless handoff to a human agent.

Data source rule (per APEX platform convention):
    NO hardcoded business data. The FAQ corpus, booking record, and policy
    rules are loaded at runtime from synthetic-data files bundled into the
    deploy ZIP under /app/data/.
"""
from __future__ import annotations
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel


import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


app = FoundryAgentApp()

MODEL_ID = "us.anthropic.claude-opus-4-6-v1"
REGION = "us-east-1"
AGENT_ID = "concierge-agent"

# Resolve the bundled data directory next to agent.py at runtime.
_AGENT_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("APEX_AE_DATA_DIR", str(_AGENT_DIR / "data")))

NEGATIVE_WORDS = [
    "frustrated", "ridiculous", "useless", "terrible", "awful", "angry",
    "unacceptable", "horrible", "disgusting",
]
HANDOFF_TRIGGERS = [
    "speak to a human", "talk to a person", "talk to an agent",
    "real person", "this is ridiculous", "manager", "frustrated", "useless",
]

SYSTEM_PROMPT = """You are ConciergeAgent, the guest-services concierge for Coral Star Cruises.

Your job: handle booking modifications and answer onboard FAQ questions, while monitoring sentiment and triggering a smooth handoff to a human agent when needed.

NON-NEGOTIABLE RULES:
1. ALWAYS sentiment_score the user message FIRST. Sentiment can override intent (frustration ⇒ handoff).
2. For policy / amenity questions (pool hours, dining, Wi-Fi, gratuities, cancellation), use rag_faq_lookup and quote the matching section verbatim — never paraphrase a policy.
3. For booking date changes:
     • If a date is provided, call booking_modify and report the staged change + applicable fee.
     • If no date is provided, ask for one (YYYY-MM-DD) and remember the pending intent.
4. Date-change fee: $0 if >30 days before sail; $75 if 14–30 days; $75 + availability disclaimer if <14 days.
5. Cancellation refund tiers: 100% (>90d) / 75% (60–89d) / 50% (30–59d) / 25% (15–29d) / 0% (<15d).
6. NEVER auto-confirm a modification — always end with "Would you like me to confirm and apply?"
7. Handoff triggers: explicit "speak to a human", sentiment ≤ -0.6, or guest mentions "manager"/"frustrated"/"unacceptable". Call agent_assist_handoff and stop.
8. If a booking_modify was pending and you answer an FAQ instead, end with: "(By the way — we were in the middle of changing your sail date. Want to come back to that when you're ready?)"
"""


# ─────────────────────── data loading ───────────────────────


def _load_text(filename: str) -> str:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Synthetic data not found: {path}")
    return path.read_text(encoding="utf-8")


def _load_json(filename: str) -> Dict[str, Any]:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Synthetic data not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


# ─────────────────────── tools ───────────────────────


@tool
def sentiment_score(message: str) -> dict:
    """Score the sentiment of a guest message on a -1.0..+1.0 scale.

    Args:
        message: The guest's message text.

    Returns:
        {"score": float, "label": "positive"|"neutral"|"negative",
         "handoff_recommended": bool}
    """
    try:
        words = message.lower().split()
        neg = sum(1 for w in words if any(n in w for n in NEGATIVE_WORDS))
        score = max(-1.0, min(1.0, -0.4 * neg))
        label = "negative" if score < -0.2 else "neutral"
        handoff = score <= -0.6 or any(t in message.lower() for t in HANDOFF_TRIGGERS)
        return {
            "status": "ok",
            "data": {
                "score": round(score, 2),
                "label": label,
                "handoff_recommended": handoff,
            },
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"sentiment_score failed: {e}"}


@tool
def rag_faq_lookup(query: str) -> dict:
    """Retrieve the most relevant section from the cruise FAQ corpus.

    Use for any policy or amenity question (pool hours, dining, gratuities,
    cancellation, Wi-Fi, etc.). Quote the returned body VERBATIM in your
    answer — never paraphrase a policy.

    Args:
        query: Guest's question.

    Returns:
        {"hit": bool, "title": str, "body": str}
    """
    try:
        text = _load_text("cruise_faq.md")
        sections: List[Tuple[str, str]] = []
        current_title = "Overview"
        current_body: List[str] = []
        for line in text.splitlines():
            if line.startswith("### "):
                if current_body:
                    sections.append((current_title, "\n".join(current_body).strip()))
                current_title = line[4:].strip()
                current_body = []
            elif line.startswith("## "):
                if current_body:
                    sections.append((current_title, "\n".join(current_body).strip()))
                current_title = line[3:].strip()
                current_body = []
            else:
                current_body.append(line)
        if current_body:
            sections.append((current_title, "\n".join(current_body).strip()))

        q_words = {w.lower() for w in re.findall(r"\w+", query) if len(w) > 2}
        scored: List[Tuple[float, str, str]] = []
        for title, body in sections:
            body_words = {w.lower() for w in re.findall(r"\w+", title + " " + body)}
            score = len(q_words & body_words) / max(len(q_words), 1)
            if score > 0:
                scored.append((score, title, body))
        scored.sort(reverse=True)
        if not scored:
            return {"status": "ok", "data": {"hit": False, "title": None, "body": None}}
        _, title, body = scored[0]
        return {"status": "ok", "data": {"hit": True, "title": title, "body": body[:600]}}
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"rag_faq_lookup failed: {e}"}


@tool
def booking_modify(new_date: str) -> dict:
    """Apply the cruise's date-change policy to the active booking.

    Args:
        new_date: New sail date in YYYY-MM-DD format.

    Returns:
        {"booking_id", "ship", "stateroom", "original_date", "new_date",
         "fee_usd", "days_to_original_sail"}
    """
    try:
        booking = _load_json("booking_record.json")
        original_date = booking["itinerary"]["embark_date"]
        try:
            new_dt = datetime.strptime(new_date, "%Y-%m-%d")
            orig_dt = datetime.strptime(original_date, "%Y-%m-%d")
        except ValueError:
            return {"status": "error", "message": "Could not parse new_date — expected YYYY-MM-DD."}

        days_to_sail = (orig_dt - datetime.utcnow()).days
        if days_to_sail >= 30:
            fee = 0
        else:
            fee = 75
        return {
            "status": "ok",
            "data": {
                "booking_id": booking["booking_id"],
                "ship": booking["ship"],
                "stateroom": booking["stateroom"],
                "original_date": original_date,
                "new_date": new_date,
                "fee_usd": fee,
                "days_to_original_sail": days_to_sail,
            },
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"booking_modify failed: {e}"}


@tool
def agent_assist_handoff() -> dict:
    """Mark the conversation as handed off to a human agent.

    Returns the booking summary + a handoff record so the human agent's
    Agent Assist Console opens with full context.

    Returns:
        {"handoff": True, "booking_summary": {...}, "ts"}
    """
    try:
        booking = _load_json("booking_record.json")
        return {
            "status": "ok",
            "data": {
                "handoff": True,
                "ts": datetime.utcnow().isoformat() + "Z",
                "booking_summary": {
                    "booking_id": booking["booking_id"],
                    "guest": (
                        f"{booking['primary_guest']['first_name']} "
                        f"{booking['primary_guest']['last_name']}"
                    ),
                    "loyalty_tier": booking["primary_guest"]["loyalty_tier"],
                    "ship": booking["ship"],
                    "stateroom": booking["stateroom"],
                    "embark_date": booking["itinerary"]["embark_date"],
                },
            },
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"agent_assist_handoff failed: {e}"}


# ─────────────────────── multi-LLM support ───────────────────────


DEFAULT_TOOL_MODEL = MODEL_ID
DEFAULT_SYNTH_MODEL = MODEL_ID
_agent_cache: Dict[tuple, Agent] = {}


def _resolve_models(model_overrides: Optional[Dict[str, Dict[str, str]]]) -> tuple:
    overrides = (model_overrides or {}).get(AGENT_ID, {})
    tool_id = overrides.get("tool_selection", DEFAULT_TOOL_MODEL)
    synth_id = overrides.get("synthesis", DEFAULT_SYNTH_MODEL)
    return tool_id, synth_id


def _get_agent(tool_model_id: str, synth_model_id: str) -> Agent:
    key = (tool_model_id, synth_model_id)
    if key in _agent_cache:
        return _agent_cache[key]
    model = AzureOpenAIModel(model_id=synth_model_id, region_name=REGION)
    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[sentiment_score, rag_faq_lookup, booking_modify, agent_assist_handoff],
    )
    _agent_cache[key] = agent
    return agent


@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_message = payload.get("prompt", "Hello")
    tool_id, synth_id = _resolve_models(payload.get("model_overrides"))
    result = _get_agent(tool_id, synth_id)(user_message)
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
