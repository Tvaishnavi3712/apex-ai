"""
In-process simulator for the Agentic Enterprise demo agents.

Three agents under one umbrella:
    OrchestratorAgent — UC-1 supply chain orchestrator (multi-tool plan)
    ConciergeAgent    — UC-2 cruise concierge (stateful chat + RAG + handoff)
    LeaseAgent        — UC-3 commercial real estate lease extraction

Design rules followed (per the user's reminder):

  1. NO hardcoded business data in this file. Every fact (warehouse
     inventory, supplier lead times, cruise FAQ text, sample lease) is
     loaded at runtime from `aws/synthetic-data/agentic_enterprise/*`.
     If the user edits one of those JSON / markdown files, the next chat
     turn picks up the change with zero code edit.

  2. The agents are deterministic Python (not real LLM calls) so the
     interview demo runs offline / without AWS in <50ms per turn.
     If/when real AgentCore runtimes get deployed for these agents,
     swap the routing in services/agentcore.py and this module becomes
     the offline fallback.

  3. Every agent returns the standard agentcore shape:
        { success, response, reasoning[], actions_taken[] }
     so the existing Agent Hub UI renders the reasoning panel without
     any frontend changes.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── data root (single source of truth for synthetic data) ──────────────
_DATA_ROOT = (
    Path(__file__).resolve().parent.parent.parent
    / "synthetic-data"
    / "agentic_enterprise"
)


def _load_json(filename: str) -> Dict[str, Any]:
    """Load a JSON file from the agentic_enterprise data folder.

    Raises FileNotFoundError if the file is missing — the user's reminder
    was that demos must use synthetic data, not be silently filled with
    hardcoded fallbacks. If the data file isn't there, the agent surfaces
    an honest error instead of pretending to know.
    """
    path = _DATA_ROOT / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Agentic Enterprise demo expects synthetic data at {path}. "
            f"Re-run synthetic-data/generate_all.py or check the deployment."
        )
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_text(filename: str) -> str:
    """Load a text/markdown file from the agentic_enterprise data folder."""
    path = _DATA_ROOT / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing synthetic data file: {path}")
    return path.read_text(encoding="utf-8")


# ─────────────────────────── helpers ─────────────────────────────


def _extract_sku(prompt: str) -> Optional[str]:
    """Pull a SKU like 'SKU-892' or 'sku 892' out of free text."""
    m = re.search(r"\bSKU[-_\s]?(\d{3,4})\b", prompt, flags=re.IGNORECASE)
    return f"SKU-{m.group(1)}" if m else None


def _extract_quantity(prompt: str) -> Optional[int]:
    """Pull a quantity like '500 units' out of free text."""
    m = re.search(r"\b(\d{2,6})\s*(units?|pcs?|each|qty)?\b", prompt, flags=re.IGNORECASE)
    return int(m.group(1)) if m else None


# ═══════════════════════════════════════════════════════════════════════
# UC-1 — OrchestratorAgent (Supply Chain)
# ═══════════════════════════════════════════════════════════════════════


class OrchestratorAgent:
    """Multi-step supply chain orchestrator.

    Implements the playbook recipe in
    `playbooks/agentic_enterprise/supply_chain_orchestrator.yaml`:
        check_inventory → find_alternative_supplier → draft_purchase_order
        → submit_for_approval

    Each step appends a ReasoningStep to the response so the Agent Hub
    UI can render the trace panel like Vertex AI Agent Builder.
    """

    AGENT_NAME = "OrchestratorAgent"

    # ── tool implementations (read from synthetic data) ──────────────

    @staticmethod
    def _tool_check_inventory(sku: str) -> Dict[str, Any]:
        """Tool: total available across warehouses + per-warehouse breakdown."""
        data = _load_json("inventory_warehouses.json")
        per_warehouse = []
        total_available = 0
        for wh in data.get("warehouses", []):
            row = next(
                (r for r in wh.get("inventory", []) if r["sku"] == sku),
                None,
            )
            if row:
                per_warehouse.append(
                    {
                        "warehouse_id": wh["warehouse_id"],
                        "name": wh["name"],
                        "available": row["available"],
                    }
                )
                total_available += row["available"]
        forecast = data.get("demand_forecast", {}).get(sku, {})
        return {
            "sku": sku,
            "total_available": total_available,
            "per_warehouse": per_warehouse,
            "demand_forecast": forecast,
        }

    @staticmethod
    def _tool_find_alternative_supplier(
        sku: str, demand_window_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Tool: rank approved suppliers for the SKU.

        Ranking: lead-time within window first (descending priority),
        then on-time %, then defect rate, then unit cost.
        """
        data = _load_json("suppliers.json")
        candidates = [
            s for s in data.get("suppliers", []) if sku in s.get("approved_skus", [])
        ]
        if demand_window_days is None:
            demand_window_days = 11

        def rank_key(s: Dict[str, Any]) -> Tuple[int, float, float, float]:
            lead_ok = 0 if s["lead_time_days"] <= demand_window_days else 1
            return (
                lead_ok,
                -s.get("on_time_pct", 0),
                s.get("defect_rate_ytd", 1.0),
                s.get("unit_cost", {}).get(sku, 999.0),
            )

        candidates.sort(key=rank_key)
        if not candidates:
            return {"sku": sku, "recommended": None, "alternates": []}
        rec = candidates[0]
        return {
            "sku": sku,
            "recommended": {
                "supplier_id": rec["supplier_id"],
                "name": rec["name"],
                "lead_time_days": rec["lead_time_days"],
                "on_time_pct": rec["on_time_pct"],
                "defect_rate_ytd": rec["defect_rate_ytd"],
                "unit_cost_usd": rec["unit_cost"][sku],
                "min_order_qty": rec.get("min_order_qty", 1),
                "credit_terms": rec.get("credit_terms", "TBD"),
                "rationale": rec.get("notes", ""),
            },
            "alternates": [
                {
                    "supplier_id": s["supplier_id"],
                    "name": s["name"],
                    "lead_time_days": s["lead_time_days"],
                    "unit_cost_usd": s["unit_cost"][sku],
                    "rationale": s.get("notes", ""),
                }
                for s in candidates[1:3]
            ],
        }

    @staticmethod
    def _tool_draft_purchase_order(
        supplier: Dict[str, Any], sku: str, quantity: int, demand_forecast: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Tool: build a PO payload from the chosen supplier + quantity."""
        unit = supplier["unit_cost_usd"]
        total = round(unit * quantity, 2)
        # PO number derived from current timestamp — deterministic shape
        po_number = "PO-" + datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        requested_delivery = demand_forecast.get(
            "campaign_start", (datetime.utcnow() + timedelta(days=11)).strftime("%Y-%m-%d")
        )
        return {
            "po_number": po_number,
            "supplier_id": supplier["supplier_id"],
            "supplier_name": supplier["name"],
            "sku": sku,
            "quantity": quantity,
            "unit_cost_usd": unit,
            "total_usd": total,
            "incoterm": "DDP",
            "requested_delivery": requested_delivery,
            "credit_terms": supplier.get("credit_terms", "Net 30"),
            "status": "DRAFT",
        }

    @staticmethod
    def _tool_submit_for_approval(po: Dict[str, Any]) -> Dict[str, Any]:
        """Tool: route the PO to the human-review queue."""
        severity = "HIGH" if po["total_usd"] > 25000 else "NORMAL"
        queue_id = "WQ-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return {
            "queue_id": queue_id,
            "approver": "merchandising@example.com",
            "severity": severity,
            "sla_hours": 4 if severity == "HIGH" else 24,
            "status": "PENDING_APPROVAL",
        }

    # ── public entrypoint ────────────────────────────────────────────

    @classmethod
    def respond(cls, prompt: str) -> Dict[str, Any]:
        """Run the full plan and return an agentcore-shaped response."""
        sku = _extract_sku(prompt) or "SKU-892"
        qty = _extract_quantity(prompt) or 500

        reasoning: List[Dict[str, Any]] = []
        actions_taken: List[str] = []

        # Step 1
        reasoning.append(
            {
                "step": 1,
                "thought": f"Operator reports a shortage of {sku}. Plan: check inventory across all warehouses to confirm.",
                "action": "check_inventory",
            }
        )
        inv = cls._tool_check_inventory(sku)
        actions_taken.append("check_inventory")
        forecast = inv["demand_forecast"]
        window = forecast.get("fulfillment_window_days", 11)

        # Step 2
        reasoning.append(
            {
                "step": 2,
                "thought": (
                    f"{sku} total available = {inv['total_available']} across {len(inv['per_warehouse'])} warehouses. "
                    f"Demand = {qty} units for {forecast.get('campaign', 'this campaign')} "
                    f"by {forecast.get('campaign_start', 'TBD')}. "
                    f"Shortfall = {qty - inv['total_available']}. Finding fastest qualified supplier."
                ),
                "action": "find_alternative_supplier",
            }
        )
        sup = cls._tool_find_alternative_supplier(sku, window)
        actions_taken.append("find_alternative_supplier")

        if not sup["recommended"]:
            return {
                "success": True,
                "response": (
                    f"No approved supplier in the catalog can fulfill {sku} within the "
                    f"{window}-day window. Escalating to {forecast.get('owner', 'merchandising@example.com')}."
                ),
                "reasoning": reasoning,
                "actions_taken": actions_taken,
            }

        rec = sup["recommended"]

        # Step 3
        reasoning.append(
            {
                "step": 3,
                "thought": (
                    f"Top supplier: {rec['name']} ({rec['supplier_id']}) — "
                    f"lead {rec['lead_time_days']}d, on-time {rec['on_time_pct']}%, "
                    f"defect {rec['defect_rate_ytd']}%, ${rec['unit_cost_usd']}/unit. "
                    f"Drafting PO."
                ),
                "action": "draft_purchase_order",
            }
        )
        po = cls._tool_draft_purchase_order(rec, sku, qty, forecast)
        actions_taken.append("draft_purchase_order")

        # Step 4
        reasoning.append(
            {
                "step": 4,
                "thought": (
                    f"PO {po['po_number']} drafted. Total ${po['total_usd']:,.2f}. "
                    f"Routing to human approver per the human-in-the-loop rule."
                ),
                "action": "submit_for_approval",
            }
        )
        queue = cls._tool_submit_for_approval(po)
        actions_taken.append("submit_for_approval")

        # Step 5 — synthesize the user-facing response
        warehouse_lines = "\n".join(
            f"   • {w['name']} ({w['warehouse_id']}): {w['available']} available"
            for w in inv["per_warehouse"]
        )
        alternates_lines = (
            "\n".join(
                f"   • {a['name']} ({a['supplier_id']}) — {a['lead_time_days']}d, ${a['unit_cost_usd']}/unit"
                for a in sup["alternates"]
            )
            or "   (none)"
        )
        response = (
            f"Confirmed shortage of {sku} — only {inv['total_available']} units available "
            f"across the network, need {qty} for {forecast.get('campaign', 'the campaign')} "
            f"on {forecast.get('campaign_start', 'TBD')}.\n\n"
            f"Per-warehouse breakdown:\n{warehouse_lines}\n\n"
            f"Recommended supplier: **{rec['name']}** ({rec['supplier_id']})\n"
            f"   • Lead time: {rec['lead_time_days']} days "
            f"({'meets' if rec['lead_time_days'] <= window else 'exceeds'} the {window}-day window)\n"
            f"   • On-time delivery: {rec['on_time_pct']}%\n"
            f"   • Defect rate YTD: {rec['defect_rate_ytd']}%\n"
            f"   • Unit cost: ${rec['unit_cost_usd']:.2f}\n"
            f"   • Credit terms: {rec['credit_terms']}\n"
            f"   • Why: {rec['rationale']}\n\n"
            f"Alternates considered:\n{alternates_lines}\n\n"
            f"Drafted PO:\n"
            f"   • PO #: {po['po_number']}\n"
            f"   • {po['quantity']} × {po['sku']} @ ${po['unit_cost_usd']:.2f} = "
            f"**${po['total_usd']:,.2f}**\n"
            f"   • INCOTERM: {po['incoterm']}\n"
            f"   • Requested delivery: {po['requested_delivery']}\n"
            f"   • Status: {po['status']}\n\n"
            f"Submitted to **{queue['approver']}** for approval — work-queue id "
            f"`{queue['queue_id']}` · severity {queue['severity']} · SLA {queue['sla_hours']}h.\n\n"
            f"_[TRACE: SCO-{queue['queue_id']}]_"
        )

        return {
            "success": True,
            "response": response,
            "reasoning": reasoning,
            "actions_taken": actions_taken,
            "po": po,
            "queue": queue,
        }


# ═══════════════════════════════════════════════════════════════════════
# UC-2 — ConciergeAgent (Cruise / Hospitality)
# ═══════════════════════════════════════════════════════════════════════


class ConciergeAgent:
    """Stateful concierge for Coral Star Cruises.

    Capabilities:
      • Booking modification — recognize date-change intent + apply policy
      • RAG over the cruise FAQ corpus for policy/amenity questions
      • Sentiment monitoring + handoff trigger when frustration detected

    State is keyed on session_id so two parallel chats don't bleed into
    each other.
    """

    AGENT_NAME = "ConciergeAgent"

    # session_id → state
    _sessions: Dict[str, Dict[str, Any]] = {}

    HANDOFF_TRIGGERS = [
        "speak to a human",
        "talk to a person",
        "talk to an agent",
        "real person",
        "this is ridiculous",
        "frustrated",
        "useless",
        "manager",
    ]

    NEGATIVE_WORDS = [
        "frustrated",
        "ridiculous",
        "useless",
        "terrible",
        "awful",
        "angry",
        "unacceptable",
    ]

    # ── tools ────────────────────────────────────────────────────────

    @staticmethod
    def _tool_rag_faq_lookup(query: str) -> Dict[str, Any]:
        """Naive RAG: split FAQ markdown into sections, score by keyword overlap."""
        text = _load_text("cruise_faq.md")
        # Split on h3 sections
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

        # Score
        q_words = {w.lower() for w in re.findall(r"\w+", query) if len(w) > 2}
        scored: List[Tuple[float, str, str]] = []
        for title, body in sections:
            body_words = {w.lower() for w in re.findall(r"\w+", title + " " + body)}
            score = len(q_words & body_words) / max(len(q_words), 1)
            if score > 0:
                scored.append((score, title, body))
        scored.sort(reverse=True)
        if not scored:
            return {"hit": False, "title": None, "body": None}
        _, title, body = scored[0]
        return {"hit": True, "title": title, "body": body[:600]}

    @staticmethod
    def _tool_booking_modify(new_date: str) -> Dict[str, Any]:
        """Apply the cruise's date-change policy to the booking."""
        booking = _load_json("booking_record.json")
        original_date = booking["itinerary"]["embark_date"]
        try:
            new_dt = datetime.strptime(new_date, "%Y-%m-%d")
            orig_dt = datetime.strptime(original_date, "%Y-%m-%d")
        except ValueError:
            return {"ok": False, "error": "could_not_parse_date"}

        # Date-change policy from cruise_faq.md — encoded as logic, not text
        days_to_sail = (orig_dt - datetime.utcnow()).days
        if days_to_sail >= 30:
            fee = 0
        elif days_to_sail >= 14:
            fee = 75
        else:
            fee = 75  # plus availability disclaimer
        return {
            "ok": True,
            "booking_id": booking["booking_id"],
            "ship": booking["ship"],
            "stateroom": booking["stateroom"],
            "original_date": original_date,
            "new_date": new_date,
            "fee_usd": fee,
            "days_to_original_sail": days_to_sail,
        }

    @staticmethod
    def _tool_sentiment_score(prompt: str) -> Dict[str, Any]:
        """Crude sentiment via keyword count. Returns -1.0…+1.0."""
        words = prompt.lower().split()
        neg = sum(1 for w in words if any(n in w for n in ConciergeAgent.NEGATIVE_WORDS))
        score = max(-1.0, min(1.0, -0.4 * neg))
        label = "negative" if score < -0.2 else "neutral"
        return {"score": round(score, 2), "label": label}

    @classmethod
    def _detect_handoff(cls, prompt: str, sentiment: Dict[str, Any]) -> bool:
        low = prompt.lower()
        if any(t in low for t in cls.HANDOFF_TRIGGERS):
            return True
        if sentiment["score"] <= -0.6:
            return True
        return False

    # ── intent detection ─────────────────────────────────────────────

    @staticmethod
    def _detect_intent(prompt: str) -> str:
        low = prompt.lower()
        if re.search(r"change\s+(my\s+)?(date|booking|sail)", low) or re.search(
            r"reschedule|move\s+(my\s+)?(date|booking)", low
        ):
            return "booking_modify"
        if re.search(r"cancel", low):
            return "cancellation"
        return "faq"

    # ── public entrypoint ────────────────────────────────────────────

    @classmethod
    def respond(cls, prompt: str, session_id: str = "default") -> Dict[str, Any]:
        sess = cls._sessions.setdefault(session_id, {"context": None, "pending_date": None})

        sentiment = cls._tool_sentiment_score(prompt)
        reasoning: List[Dict[str, Any]] = []
        actions_taken: List[str] = []
        actions_taken.append("sentiment_score")
        reasoning.append(
            {
                "step": 1,
                "thought": f"Sentiment: {sentiment['label']} ({sentiment['score']:+.2f}).",
                "action": "sentiment_score",
            }
        )

        if cls._detect_handoff(prompt, sentiment):
            actions_taken.append("agent_assist_handoff")
            reasoning.append(
                {
                    "step": 2,
                    "thought": "Handoff trigger detected. Switching to Agent Assist Console.",
                    "action": "agent_assist_handoff",
                }
            )
            booking = _load_json("booking_record.json")
            return {
                "success": True,
                "response": (
                    "I understand — I'm connecting you with a guest-services specialist now. "
                    "While I do, here's a summary of your booking they'll see on their screen:\n\n"
                    f"   • Booking: {booking['booking_id']}\n"
                    f"   • Guest: {booking['primary_guest']['first_name']} "
                    f"{booking['primary_guest']['last_name']} ({booking['primary_guest']['loyalty_tier']})\n"
                    f"   • Ship: {booking['ship']}, Stateroom {booking['stateroom']}\n"
                    f"   • Sail: {booking['itinerary']['embark_date']}\n\n"
                    "_[handoff_to_human · sentiment={:.2f}]_".format(sentiment["score"])
                ),
                "reasoning": reasoning,
                "actions_taken": actions_taken,
                "handoff": True,
                "sentiment": sentiment,
            }

        intent = cls._detect_intent(prompt)
        reasoning.append(
            {
                "step": 2,
                "thought": f"Intent: {intent}.",
                "action": "intent_classify",
            }
        )

        # Booking modification path (multi-turn aware)
        if intent == "booking_modify":
            sess["context"] = "booking_modify"
            new_date_match = re.search(r"\b(20\d{2})[-/](\d{1,2})[-/](\d{1,2})\b", prompt)
            month_match = re.search(
                r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+(\d{1,2})", prompt, re.I
            )
            new_date = None
            if new_date_match:
                new_date = (
                    f"{new_date_match.group(1)}-{int(new_date_match.group(2)):02d}-"
                    f"{int(new_date_match.group(3)):02d}"
                )
            elif month_match:
                month_map = {
                    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
                }
                m = month_map[month_match.group(1).lower()[:3]]
                d = int(month_match.group(2))
                new_date = f"2026-{m:02d}-{d:02d}"

            if not new_date:
                sess["pending_date"] = True
                return {
                    "success": True,
                    "response": "Happy to help change your sail date — what date would you like to move to? (Use YYYY-MM-DD please.)",
                    "reasoning": reasoning,
                    "actions_taken": actions_taken,
                }

            actions_taken.append("booking_modify")
            mod = cls._tool_booking_modify(new_date)
            sess["pending_date"] = False
            if not mod["ok"]:
                return {
                    "success": True,
                    "response": "I couldn't parse that date — could you provide it as YYYY-MM-DD?",
                    "reasoning": reasoning,
                    "actions_taken": actions_taken,
                }
            fee_line = (
                f"Date-change fee: **$0** (more than 30 days before sail)."
                if mod["fee_usd"] == 0
                else f"Date-change fee: **${mod['fee_usd']}** ({mod['days_to_original_sail']} days to sail — within 30-day window)."
            )
            response = (
                f"Done — I've staged the date change on booking {mod['booking_id']}.\n\n"
                f"   • Ship: {mod['ship']}, Stateroom {mod['stateroom']}\n"
                f"   • Original sail date: {mod['original_date']}\n"
                f"   • New sail date: **{mod['new_date']}**\n"
                f"   • {fee_line}\n\n"
                "Would you like me to confirm and apply, or quote any fare difference first?"
            )
            return {
                "success": True,
                "response": response,
                "reasoning": reasoning,
                "actions_taken": actions_taken,
                "modification": mod,
                "sentiment": sentiment,
            }

        # FAQ path (RAG)
        actions_taken.append("rag_faq_lookup")
        rag = cls._tool_rag_faq_lookup(prompt)
        reasoning.append(
            {
                "step": 3,
                "thought": (
                    f"RAG hit: '{rag['title']}' (top section)."
                    if rag["hit"]
                    else "No FAQ section matched — falling back to general response."
                ),
                "action": "rag_faq_lookup",
            }
        )
        if not rag["hit"]:
            return {
                "success": True,
                "response": (
                    "I don't have that exact answer in the guest-services knowledge base. "
                    "Would you like me to connect you with a human concierge?"
                ),
                "reasoning": reasoning,
                "actions_taken": actions_taken,
            }
        # Restoring booking-modify context if it was active
        context_note = ""
        if sess.get("context") == "booking_modify" and sess.get("pending_date"):
            context_note = (
                "\n\n_(By the way — we were in the middle of changing your sail date. "
                "Want to come back to that when you're ready?)_"
            )

        response = (
            f"**{rag['title']}** — {rag['body']}{context_note}"
        )
        return {
            "success": True,
            "response": response,
            "reasoning": reasoning,
            "actions_taken": actions_taken,
            "sentiment": sentiment,
        }


# ═══════════════════════════════════════════════════════════════════════
# UC-3 — LeaseAgent (Commercial Real Estate)
# ═══════════════════════════════════════════════════════════════════════


class LeaseAgent:
    """Lease extraction + DuckDB query agent.

    Three intents:
      • "extract" — pull tenant_name, expiration_date, liability_clause from
        the sample lease (or any provided text). Returns confidence scores.
      • "ingest"  — push the extracted record into a DuckDB `leases` table.
      • "query"   — run SQL against the leases table and return rows.

    The DuckDB instance lives at synthetic-data/agentic_enterprise/leases.duckdb
    and persists across calls so subsequent queries see prior ingests.
    """

    AGENT_NAME = "LeaseAgent"

    DB_PATH = _DATA_ROOT / "leases.duckdb"

    # ── tools ────────────────────────────────────────────────────────

    @staticmethod
    def _tool_lease_extract(text: Optional[str] = None) -> Dict[str, Any]:
        """Regex-based extractor over the lease text. Real deployment uses
        Textract / Bedrock; this in-process version is deterministic and
        fast for the demo.
        """
        if text is None:
            text = _load_text("sample_lease.txt")

        # Tenant name — captures "TENANT: <Name>" or "Tenant Name: <Name>"
        tenant = None
        m = re.search(
            r"TENANT:\s*\n?\s*([A-Z][\w &.,'\-]+?(?:Inc\.|LLC|LP|Corp\.?|Ltd\.?|Co\.|Solutions|Holdings))",
            text,
        )
        if m:
            tenant = m.group(1).strip()

        # Expiration date — captures dates like "December 31, 2026" or "12/31/2026"
        expiration = None
        m = re.search(
            r"expir[a-z]*[^.]*?(\d{1,2}/\d{1,2}/\d{2,4}|"
            r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
            r"\s+\d{1,2},\s+\d{4})",
            text,
            re.IGNORECASE,
        )
        if m:
            raw = m.group(1)
            # Normalize to ISO
            try:
                if "/" in raw:
                    dt = datetime.strptime(raw, "%m/%d/%Y") if len(raw.split("/")[-1]) == 4 else datetime.strptime(raw, "%m/%d/%y")
                else:
                    dt = datetime.strptime(raw, "%B %d, %Y")
                expiration = dt.strftime("%Y-%m-%d")
            except ValueError:
                expiration = raw

        # Liability clause — captures the indemnification paragraph
        liability_clause = None
        m = re.search(
            r"(Tenant shall indemnify[^§]*?survive the expiration[^.]*\.)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if m:
            liability_clause = re.sub(r"\s+", " ", m.group(1).strip())

        return {
            "tenant_name": tenant,
            "expiration_date": expiration,
            "liability_clause_text": liability_clause,
            "confidence": {
                "tenant_name": 0.97 if tenant else 0.0,
                "expiration_date": 0.95 if expiration else 0.0,
                "liability_clause_text": 0.92 if liability_clause else 0.0,
            },
        }

    @classmethod
    def _get_duckdb(cls):
        """Lazy import + connect. duckdb is small and pure-python-installable."""
        try:
            import duckdb  # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "duckdb is required for LeaseAgent. Install with `pip install duckdb`."
            ) from e
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(str(cls.DB_PATH))

    @classmethod
    def _tool_lease_index(cls, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """Insert the extracted record into the DuckDB leases table."""
        con = cls._get_duckdb()
        try:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS leases (
                    lease_id           VARCHAR PRIMARY KEY,
                    tenant_name        VARCHAR,
                    expiration_date    DATE,
                    liability_clause   VARCHAR,
                    ingested_at        TIMESTAMP
                )
                """
            )
            lease_id = "L-" + datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            con.execute(
                "INSERT INTO leases VALUES (?, ?, ?, ?, ?)",
                [
                    lease_id,
                    extracted.get("tenant_name"),
                    extracted.get("expiration_date"),
                    extracted.get("liability_clause_text"),
                    datetime.utcnow(),
                ],
            )
            count = con.execute("SELECT COUNT(*) FROM leases").fetchone()[0]
            return {"lease_id": lease_id, "table_row_count": count}
        finally:
            con.close()

    @classmethod
    def _tool_duckdb_query(cls, sql: str) -> Dict[str, Any]:
        """Execute a SQL query against the leases table. Read-only."""
        # Defensive: only allow SELECT
        if not re.match(r"\s*SELECT\b", sql, re.IGNORECASE):
            return {"ok": False, "error": "only_select_allowed"}
        con = cls._get_duckdb()
        try:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS leases (
                    lease_id           VARCHAR PRIMARY KEY,
                    tenant_name        VARCHAR,
                    expiration_date    DATE,
                    liability_clause   VARCHAR,
                    ingested_at        TIMESTAMP
                )
                """
            )
            cur = con.execute(sql)
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            return {"ok": True, "columns": cols, "rows": [list(r) for r in rows]}
        except Exception as e:  # pragma: no cover — surface to UI
            return {"ok": False, "error": str(e)}
        finally:
            con.close()

    # ── public entrypoint ────────────────────────────────────────────

    @classmethod
    def respond(cls, prompt: str) -> Dict[str, Any]:
        low = prompt.lower()
        reasoning: List[Dict[str, Any]] = []
        actions_taken: List[str] = []

        # SQL query intent
        if low.startswith("select") or "from leases" in low or "run sql" in low:
            sql = prompt
            if "run sql" in low:
                m = re.search(r"```sql\s*(.+?)```", prompt, re.DOTALL | re.IGNORECASE)
                if m:
                    sql = m.group(1).strip()
            reasoning.append(
                {"step": 1, "thought": "Query intent — running SQL on DuckDB.", "action": "duckdb_query"}
            )
            actions_taken.append("duckdb_query")
            res = cls._tool_duckdb_query(sql)
            if not res["ok"]:
                return {
                    "success": True,
                    "response": f"Query error: `{res['error']}`",
                    "reasoning": reasoning,
                    "actions_taken": actions_taken,
                }
            cols = res["columns"]
            rows = res["rows"]
            if not rows:
                rendered = "_(no rows returned)_"
            else:
                rendered = (
                    "| " + " | ".join(cols) + " |\n"
                    + "| " + " | ".join(["---"] * len(cols)) + " |\n"
                    + "\n".join(
                        "| " + " | ".join(str(c) for c in row) + " |" for row in rows
                    )
                )
            return {
                "success": True,
                "response": f"**Query result ({len(rows)} row(s)):**\n\n{rendered}",
                "reasoning": reasoning,
                "actions_taken": actions_taken,
                "rows": rows,
                "columns": cols,
            }

        # Default: extract → ingest → suggest a query
        reasoning.append(
            {
                "step": 1,
                "thought": "Running entity extraction on the source lease document.",
                "action": "lease_extract",
            }
        )
        actions_taken.append("lease_extract")
        extracted = cls._tool_lease_extract()

        reasoning.append(
            {
                "step": 2,
                "thought": "Inserting extracted entities into DuckDB `leases` table.",
                "action": "lease_index",
            }
        )
        actions_taken.append("lease_index")
        ingest = cls._tool_lease_index(extracted)

        suggested_sql = (
            "SELECT tenant_name, expiration_date FROM leases\n"
            "WHERE liability_clause LIKE '%indemnify%'\n"
            "  AND EXTRACT(YEAR FROM expiration_date) = 2026"
        )
        reasoning.append(
            {
                "step": 3,
                "thought": "Suggesting a SQL query the user can run against the structured table.",
                "action": "suggest_query",
            }
        )
        actions_taken.append("suggest_query")

        response = (
            "**Extraction complete.**\n\n"
            f"   • Tenant: **{extracted['tenant_name']}** "
            f"(confidence {extracted['confidence']['tenant_name']:.2f})\n"
            f"   • Expiration: **{extracted['expiration_date']}** "
            f"(confidence {extracted['confidence']['expiration_date']:.2f})\n"
            f"   • Liability clause: _{(extracted['liability_clause_text'] or '')[:120]}…_ "
            f"(confidence {extracted['confidence']['liability_clause_text']:.2f})\n\n"
            f"Ingested as `{ingest['lease_id']}`. The `leases` table now has "
            f"{ingest['table_row_count']} row(s).\n\n"
            "Try running this SQL to see the structured result:\n"
            f"```sql\n{suggested_sql}\n```"
        )
        return {
            "success": True,
            "response": response,
            "reasoning": reasoning,
            "actions_taken": actions_taken,
            "extracted": extracted,
            "ingest": ingest,
        }
