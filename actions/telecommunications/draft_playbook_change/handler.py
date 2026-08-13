"""
draft_playbook_change — Verizon CAS far-edge orchestration action (demo stub).
Draft a single playbook role change with diff + reason + risk.
"""
import os, sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="draft_playbook_change",
    description="Draft a single playbook role change with diff + reason + risk.",
    category="telco_far_edge",
    industry="telecommunications",
    input_schema=ActionInputSchema(description="draft_playbook_change input")
        .add_string("platform", "Target platform / new server type", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="draft_playbook_change output")
        .add_string("role", "Role")
        .add_string("required_change", "Required Change")
        .add_string("reason", "Reason")
        .add_string("risk", "Risk")
))
def draft_playbook_change(platform: str = None, context: str = None) -> dict:
    """Stub: returns a CAS-realistic payload for the demo."""
    payload = {'role': 'group_vars/HPE', 'required_change': 'add bios_attribute_value_workload_profile_vRAN: vRAN', 'reason': 'iLO7 rejects other WorkloadProfile values', 'risk': 'low'}
    payload["generated_at"] = datetime.utcnow().isoformat()
    return payload
