"""
Apex Agentic Enterprise — LeaseAgent (UC-3, vendor-neutral demo).

Document AI pipeline that extracts tenant + expiration + liability clause
from commercial lease agreements, ingests them into a DuckDB `leases`
table, and answers SQL queries against the table.

Data source rule (per APEX platform convention):
    NO hardcoded business data. The sample lease text is loaded at runtime
    from the synthetic-data file bundled into the deploy ZIP under
    /app/data/sample_lease.txt.
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
AGENT_ID = "lease-agent"

# Resolve the bundled data directory next to agent.py at runtime.
_AGENT_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("APEX_AE_DATA_DIR", str(_AGENT_DIR / "data")))
DUCKDB_PATH = Path(os.environ.get("APEX_AE_DUCKDB_PATH", "/tmp/leases.duckdb"))

SYSTEM_PROMPT = """You are LeaseAgent, a commercial real estate document intelligence agent.

Your job: turn unstructured lease PDFs into queryable rows in a DuckDB `leases` table, and answer SQL queries against that table.

NON-NEGOTIABLE RULES:
1. ALWAYS show per-field confidence scores for extractions. Reviewers don't trust black-box extraction.
2. Confidence < 0.7 on any required field ⇒ flag for human review, do not auto-ingest.
3. Only SELECT queries are permitted against the leases table — reject any DML.
4. When a user asks a question that maps to a SQL query (e.g., "leases expiring in 2026"), generate the SQL, run duckdb_query, and show BOTH the SQL and the result.
5. After each successful extract+ingest, suggest a starter query like:
     SELECT tenant_name, expiration_date FROM leases
     WHERE liability_clause LIKE '%indemnify%'
       AND EXTRACT(YEAR FROM expiration_date) = 2026

Tool plan for extraction requests: lease_extract → lease_index → suggest a query.
Tool plan for SQL requests: duckdb_query → render results as Markdown table.
"""


# ─────────────────────── data + db ───────────────────────


def _load_text(filename: str) -> str:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Synthetic data not found: {path}")
    return path.read_text(encoding="utf-8")


def _get_duckdb():
    import duckdb  # type: ignore

    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DUCKDB_PATH))
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
    return con


# ─────────────────────── tools ───────────────────────


@tool
def lease_extract(text: Optional[str] = None) -> dict:
    """Extract tenant_name, expiration_date, and liability_clause_text from a lease.

    If `text` is None, defaults to the bundled sample_lease.txt for demo.
    Each field comes back with a confidence score (0..1).

    Args:
        text: Raw lease text. None to use the bundled sample.

    Returns:
        {"tenant_name", "expiration_date", "liability_clause_text",
         "confidence": {field_name -> 0..1}}
    """
    try:
        if text is None:
            text = _load_text("sample_lease.txt")

        tenant = None
        m = re.search(
            r"TENANT:\s*\n?\s*([A-Z][\w &.,'\-]+?(?:Inc\.|LLC|LP|Corp\.?|Ltd\.?|Co\.|Solutions|Holdings))",
            text,
        )
        if m:
            tenant = m.group(1).strip()

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
            try:
                if "/" in raw:
                    fmt = "%m/%d/%Y" if len(raw.split("/")[-1]) == 4 else "%m/%d/%y"
                    dt = datetime.strptime(raw, fmt)
                else:
                    dt = datetime.strptime(raw, "%B %d, %Y")
                expiration = dt.strftime("%Y-%m-%d")
            except ValueError:
                expiration = raw

        liability_clause = None
        m = re.search(
            r"(Tenant shall indemnify[^§]*?survive the expiration[^.]*\.)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if m:
            liability_clause = re.sub(r"\s+", " ", m.group(1).strip())

        return {
            "status": "ok",
            "data": {
                "tenant_name": tenant,
                "expiration_date": expiration,
                "liability_clause_text": liability_clause,
                "confidence": {
                    "tenant_name": 0.97 if tenant else 0.0,
                    "expiration_date": 0.95 if expiration else 0.0,
                    "liability_clause_text": 0.92 if liability_clause else 0.0,
                },
            },
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"lease_extract failed: {e}"}


@tool
def lease_index(
    tenant_name: str, expiration_date: str, liability_clause_text: str
) -> dict:
    """Insert an extracted lease record into the DuckDB leases table.

    Args:
        tenant_name: Legal name of the tenant.
        expiration_date: ISO date (YYYY-MM-DD).
        liability_clause_text: Verbatim liability/indemnification clause text.

    Returns:
        {"lease_id", "table_row_count"}
    """
    try:
        con = _get_duckdb()
        try:
            lease_id = "L-" + datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            con.execute(
                "INSERT INTO leases VALUES (?, ?, ?, ?, ?)",
                [
                    lease_id,
                    tenant_name,
                    expiration_date,
                    liability_clause_text,
                    datetime.utcnow(),
                ],
            )
            count = con.execute("SELECT COUNT(*) FROM leases").fetchone()[0]
            return {
                "status": "ok",
                "data": {"lease_id": lease_id, "table_row_count": count},
            }
        finally:
            con.close()
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"lease_index failed: {e}"}


@tool
def duckdb_query(sql: str) -> dict:
    """Execute a SELECT query against the DuckDB leases table.

    Args:
        sql: SELECT statement. DML (INSERT/UPDATE/DELETE/DROP) is rejected.

    Returns:
        {"columns": [...], "rows": [[...], ...]}
    """
    try:
        if not re.match(r"\s*SELECT\b", sql, re.IGNORECASE):
            return {"status": "error", "message": "Only SELECT statements are allowed."}
        con = _get_duckdb()
        try:
            cur = con.execute(sql)
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            return {
                "status": "ok",
                "data": {"columns": cols, "rows": [list(r) for r in rows]},
            }
        finally:
            con.close()
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"duckdb_query failed: {e}"}


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
        tools=[lease_extract, lease_index, duckdb_query],
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
