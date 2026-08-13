#!/usr/bin/env python3
"""
Provision Apex agents into Azure AI Foundry Agent Service.

Azure replacement for the AWS deploy script. Where that zipped agent code to
object storage and created a managed runtime, this script
registers each agent as a **persistent Foundry agent** — instructions plus tool
schemas — and writes back the id mapping the backend uses at runtime.

Usage
-----
    az login
    export AZURE_AI_PROJECT_ENDPOINT="https://<project>.services.ai.azure.com/api/projects/<name>"
    export AZURE_OPENAI_DEPLOYMENT="gpt-5.4"

    python deploy_foundry_agents.py --list
    python deploy_foundry_agents.py --agent apex-contract-bot
    python deploy_foundry_agents.py --all

On success it writes `foundry_agents.json` — the map the backend reads via
`AZURE_FOUNDRY_AGENTS`:

    export AZURE_FOUNDRY_AGENTS="$(cat foundry-agents/foundry_agents.json)"

Note: agents run happily WITHOUT this step. Any agent that has no Foundry id
falls back to the in-process runtime (`foundry_runtime.Agent`), which is the
path the demos use.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
MAP_FILE = ROOT / "foundry_agents.json"


def discover() -> List[Path]:
    """Every directory containing an agent.py."""
    return sorted(p.parent for p in ROOT.glob("*/agent.py"))


def load_agent_module(agent_dir: Path):
    """Import an agent.py in isolation and hand back its module."""
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(agent_dir))
    spec = importlib.util.spec_from_file_location(f"apex_{agent_dir.name}", agent_dir / "agent.py")
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {agent_dir/'agent.py'}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def describe(agent_dir: Path) -> Optional[Dict[str, Any]]:
    """Extract name / instructions / model / tool schemas from an agent module."""
    try:
        mod = load_agent_module(agent_dir)
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠️  {agent_dir.name}: import failed — {e}")
        return None

    # Preferred: a module-level `agent`. Otherwise fall back to the app's agent,
    # then to synthesising one from SYSTEM_PROMPT + @tool functions — some agents
    # build their Agent inside a factory function, so nothing is module-level.
    agent = getattr(mod, "agent", None)
    if agent is None:
        agent = getattr(getattr(mod, "app", None), "agent", None)

    if agent is not None:
        instructions = getattr(agent, "system_prompt", "") or ""
        model = getattr(getattr(agent, "model", None), "deployment", None)
        tools = getattr(agent, "tool_schemas", [])
    else:
        instructions = getattr(mod, "SYSTEM_PROMPT", "") or ""
        model = getattr(getattr(mod, "model", None), "deployment", None)
        tools = [
            getattr(fn, "__tool_schema__")
            for fn in vars(mod).values()
            if callable(fn) and hasattr(fn, "__tool_schema__")
        ]
        if not instructions and not tools:
            print(f"  ⚠️  {agent_dir.name}: no agent, SYSTEM_PROMPT, or @tool functions found")
            return None
        print(f"  ℹ️  {agent_dir.name}: synthesised from module scope (factory-built agent)")

    return {
        "name": agent_dir.name,
        "instructions": instructions,
        "model": model or os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4"),
        "tools": tools,
    }


def get_client():
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
    if not endpoint:
        sys.exit(
            "AZURE_AI_PROJECT_ENDPOINT is not set.\n"
            "  Find it in the Azure AI Foundry portal under Project → Overview."
        )
    return AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())


def provision(spec: Dict[str, Any], existing: Dict[str, str]) -> Optional[str]:
    """Create or update one Foundry agent; returns its id."""
    client = get_client()
    name = spec["name"]
    payload = dict(
        model=spec["model"],
        name=name,
        instructions=spec["instructions"][:250_000],
        tools=spec["tools"] or None,
    )
    try:
        if name in existing:
            agent = client.agents.update_agent(agent_id=existing[name], **payload)
            action = "updated"
        else:
            agent = client.agents.create_agent(**payload)
            action = "created"
        print(f"  ✅ {name}: {action} ({agent.id}) · model={spec['model']} · tools={len(spec['tools'])}")
        return agent.id
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ {name}: {e}")
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="Provision Apex agents into Azure AI Foundry.")
    ap.add_argument("--all", action="store_true", help="provision every discovered agent")
    ap.add_argument("--agent", action="append", default=[], help="agent directory name (repeatable)")
    ap.add_argument("--list", action="store_true", help="list agents and their tool counts")
    args = ap.parse_args()

    dirs = discover()
    if not dirs:
        sys.exit("No agents found (expected */agent.py).")

    if args.list:
        print(f"{len(dirs)} agents:\n")
        for d in dirs:
            spec = describe(d)
            if spec:
                print(f"  {spec['name']:32s} model={spec['model']:12s} tools={len(spec['tools'])}")
        return

    if args.agent:
        dirs = [d for d in dirs if d.name in set(args.agent)]
        if not dirs:
            sys.exit("None of the requested agents were found.")
    elif not args.all:
        ap.print_help()
        sys.exit("\nChoose --all, --agent <name>, or --list.")

    existing: Dict[str, str] = {}
    if MAP_FILE.exists():
        try:
            existing = json.loads(MAP_FILE.read_text())
        except json.JSONDecodeError:
            pass

    print(f"Provisioning {len(dirs)} agent(s) into Azure AI Foundry…\n")
    for d in dirs:
        spec = describe(d)
        if not spec:
            continue
        agent_id = provision(spec, existing)
        if agent_id:
            existing[spec["name"]] = agent_id

    MAP_FILE.write_text(json.dumps(existing, indent=2))
    print(f"\n📝 wrote {MAP_FILE.relative_to(ROOT.parent)} ({len(existing)} agents)")
    print("   Point the backend at them with:")
    print(f'   export AZURE_FOUNDRY_AGENTS="$(cat {MAP_FILE})"')


if __name__ == "__main__":
    main()
