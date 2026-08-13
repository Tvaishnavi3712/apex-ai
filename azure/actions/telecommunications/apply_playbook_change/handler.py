"""
apply_playbook_change — Verizon CAS far-edge orchestration action (demo stub).
Commit approved changes + open a PR (DIRECT ACTION — HITL-gated).
"""
import os, sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="apply_playbook_change",
    description="Commit approved changes + open a PR (DIRECT ACTION — HITL-gated).",
    category="telco_far_edge",
    industry="telecommunications",
    input_schema=ActionInputSchema(description="apply_playbook_change input")
        .add_string("platform", "Target platform / new server type", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="apply_playbook_change output")
        .add_string("branch", "Branch")
        .add_string("pr", "Pr")
        .add_string("files_changed", "Files Changed")
        .add_string("requires_hitl", "Requires Hitl")
))
def apply_playbook_change(platform: str = None, context: str = None) -> dict:
    """Stub: returns a CAS-realistic payload for the demo."""
    payload = {'branch': 'el140-ilo7-support', 'pr': 'draft', 'files_changed': 15, 'requires_hitl': True}
    payload["generated_at"] = datetime.utcnow().isoformat()
    return payload
