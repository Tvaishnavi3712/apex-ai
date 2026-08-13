# Apex STP PolicyAgent

UC-1 specialist for ChatSTP — answers STP Nuclear Operating Company policy and
procedure questions with verbatim citations.

## What it does

- Searches an embedded STP policy corpus (STP-415, STP-OP-2204, STP-MNT-1102,
  STP-RAD-901, ...).
- Returns the answer in plain English plus a verbatim `Source:` line including
  doc-number, section, effective date, and exact quoted text.
- Refuses to fabricate policies — if no match is found, it says so.

## Tools

| Tool | Purpose |
|------|---------|
| `search_policies(query, top_k=3)` | Keyword/BM25-ish search over corpus |
| `extract_citation(doc_id, topic)` | Pull the verbatim section text for a doc |

## Demo question

> What is the max meal allowance for site-meeting business travel?

Expected pattern (must cite `STP-415 § 3.2` verbatim):

```
The maximum meal allowance for site-meeting business travel is $75 per day.

Source: STP-415 § 3.2 (effective 2024-06-01): "Per-diem meal allowance for on-site
business meetings shall not exceed $75.00 per traveler per calendar day,
inclusive of gratuity."
```

## Test locally

```bash
cd foundry_agent-agents/apex-stp-policy-agent
pip install -r requirements.txt
python test_local.py
```

## Deploy

Use the shared deployment script (idempotent, dry-run by default):

```bash
cd foundry_agent-agents
python deploy_stp_agents.py            # prints plan
python deploy_stp_agents.py --apply    # actually deploys
```

## Model

- `us.anthropic.claude-opus-4-6-v1` (Azure OpenAI inference profile — required for on-demand)
- Region: `us-east-1`
