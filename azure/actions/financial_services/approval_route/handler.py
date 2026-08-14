"""
Approval Route - Small Factory (Context-Driven)
Determines approval routing based on invoice amount and policy.

Context-Driven Architecture:
- Approval thresholds are read from playbook context.approval_workflow
- GL code mappings are read from playbook context.gl_mappings
- Department rules are read from playbook context
"""

from typing import Dict, Any, List, Optional
import structlog

try:
    from services.small_factory import register_factory
    SMALL_FACTORY_ENABLED = True
except ImportError:
    SMALL_FACTORY_ENABLED = False
    def register_factory(name):
        def decorator(func):
            return func
        return decorator

logger = structlog.get_logger()


# Default approval matrix (used when context not provided)
DEFAULT_APPROVAL_MATRIX = {
    "auto_approve": {
        "max_amount": 500,
        "requires_po": True,
        "variance_tolerance": 0.02,
    },
    "manager": {
        "max_amount": 5000,
        "approver_role": "department_manager",
        "sla_hours": 24,
    },
    "director": {
        "max_amount": 25000,
        "approver_role": "department_director",
        "sla_hours": 48,
    },
    "vp": {
        "max_amount": 100000,
        "approver_role": "vp_finance",
        "sla_hours": 72,
    },
    "cfo": {
        "max_amount": float('inf'),
        "approver_role": "cfo",
        "sla_hours": 96,
    },
}

# Default GL code to department mapping
DEFAULT_GL_DEPARTMENT_MAP = {
    "6100": {"department": "operations", "cost_center": "CC-100"},
    "6150": {"department": "admin", "cost_center": "CC-150"},
    "6200": {"department": "technology", "cost_center": "CC-200"},
    "6300": {"department": "marketing", "cost_center": "CC-300"},
    "6400": {"department": "sales", "cost_center": "CC-400"},
}


def determine_approval_level(
    amount: float,
    has_variance: bool,
    is_new_vendor: bool,
    approval_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Determine required approval level using context configuration."""
    thresholds = approval_config.get("thresholds", DEFAULT_APPROVAL_MATRIX)

    # Check auto-approve conditions
    auto_config = thresholds.get("auto_approve", {})
    auto_max = auto_config.get("max_amount", 500)
    auto_conditions = auto_config.get("conditions", {})

    can_auto_approve = (
        amount <= auto_max and
        not has_variance and
        not is_new_vendor
    )

    # Additional auto-approve conditions from context
    if auto_conditions:
        if auto_conditions.get("no_exceptions") and (has_variance or is_new_vendor):
            can_auto_approve = False
        if auto_conditions.get("po_matched") is True:
            # Would need PO status from input
            pass

    if can_auto_approve:
        return {
            "level": "auto_approve",
            "approver_role": None,
            "sla_hours": 0,
            "auto_process": True,
        }

    # Find appropriate approval level based on amount
    approval_levels = ["team_lead", "supervisor", "manager", "director", "vp_finance", "cfo", "board"]

    for level in approval_levels:
        config = thresholds.get(level, {})
        if not config:
            continue

        max_amount = config.get("max_amount", float('inf'))
        if amount <= max_amount:
            return {
                "level": level,
                "approver_role": config.get("approvers", [level])[0] if config.get("approvers") else level,
                "sla_hours": config.get("sla_hours", 48),
                "auto_process": False,
                "dual_approval": config.get("dual_approval", False),
            }

    # Default to highest level
    return {
        "level": "cfo",
        "approver_role": "cfo",
        "sla_hours": 96,
        "auto_process": False,
    }


def get_additional_approvers(
    flags: List[str],
    approval_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Determine additional approvers based on flags and context rules."""
    additional = []

    # Get additional approver rules from context
    additional_rules = approval_config.get("additional_approvers", {})

    if "new_vendor" in flags:
        vendor_rule = additional_rules.get("new_vendor", {})
        additional.append({
            "role": vendor_rule.get("role", "vendor_management"),
            "reason": vendor_rule.get("reason", "New vendor requires vendor management approval"),
            "required": vendor_rule.get("required", True),
        })

    if "variance_high" in flags:
        variance_rule = additional_rules.get("variance_high", {})
        additional.append({
            "role": variance_rule.get("role", "procurement"),
            "reason": variance_rule.get("reason", "Significant variance from PO"),
            "required": variance_rule.get("required", False),
        })

    if "compliance_warning" in flags:
        compliance_rule = additional_rules.get("compliance_warning", {})
        additional.append({
            "role": compliance_rule.get("role", "compliance_officer"),
            "reason": compliance_rule.get("reason", "Compliance warning requires review"),
            "required": compliance_rule.get("required", True),
        })

    return additional


def get_gl_department(
    gl_code: str,
    gl_mappings: Dict[str, Any]
) -> Dict[str, str]:
    """Get department info from GL code using context mappings."""
    if gl_mappings and gl_code in gl_mappings:
        mapping = gl_mappings[gl_code]
        return {
            "department": mapping.get("department", "general"),
            "cost_center": mapping.get("cost_center", "CC-000"),
        }

    # Fall back to default mappings
    return DEFAULT_GL_DEPARTMENT_MAP.get(
        gl_code,
        {"department": "general", "cost_center": "CC-000"}
    )


@register_factory("approval_route")
async def approval_route(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Determine approval routing for invoice (context-driven).

    Context keys used:
        - approval_workflow: Approval thresholds and rules
        - gl_mappings: GL code to department mappings

    Args:
        input_data: Invoice and vendor data from previous factories
        context: Playbook context with approval rules

    Returns:
        Approval routing decision
    """
    context = context or input_data.get("context", {})
    config = input_data.get('config', {})
    invoice = input_data.get('invoice_extract', {}) or input_data.get('data_extraction', {})
    vendor = input_data.get('vendor_match', {}) or input_data.get('vendor_validation', {})
    po_result = input_data.get('po_reconcile', {}) or input_data.get('po_matching', {})
    compliance = input_data.get('compliance_check', {})

    # Get approval configuration from context
    approval_config = context.get("approval_workflow", {})
    gl_mappings = context.get("gl_mappings", {})

    logger.info(
        "Approval routing invoked",
        context_driven=bool(context),
        has_approval_config=bool(approval_config)
    )

    amount = invoice.get('total_amount', 0) or invoice.get('total', 0)
    flags = []

    # Check for new vendor flag
    if vendor.get('new_vendor') or vendor.get('status') == 'pending':
        flags.append("new_vendor")

    # Check for variance issues
    variance = po_result.get('variance', {})
    if variance and not variance.get('within_tolerance', True):
        variance_pct = abs(variance.get('variance_percent', 0))
        variance_threshold = approval_config.get("variance_threshold_percent", 10)
        if variance_pct > variance_threshold:
            flags.append("variance_high")

    # Check for compliance issues
    if compliance.get('compliance_status') == 'WARNING':
        flags.append("compliance_warning")
    if compliance.get('compliance_status') == 'FAIL':
        flags.append("compliance_fail")

    has_variance = "variance_high" in flags
    is_new_vendor = "new_vendor" in flags

    # Determine approval level from context
    approval = determine_approval_level(amount, has_variance, is_new_vendor, approval_config)
    additional_approvers = get_additional_approvers(flags, approval_config)

    # Build approvers list
    approvers = []
    if approval["approver_role"]:
        approvers.append({
            "role": approval["approver_role"],
            "sequence": 1,
            "required": True
        })

    for i, add in enumerate(additional_approvers):
        add["sequence"] = i + 2
        approvers.append(add)

    # Check dual approval requirement from context
    dual_approval_config = approval_config.get("dual_approval", {})
    dual_threshold = dual_approval_config.get("required_above", 100000)
    if amount > dual_threshold and approval.get("dual_approval", True):
        flags.append("dual_approval_required")

    # Get GL code and department info
    gl_code = vendor.get('default_gl_code', '6100')
    department = get_gl_department(gl_code, gl_mappings)

    # Generate workflow ID
    workflow_id = f"INV-{approval['level'].upper()}-{len(approvers)}"

    # Determine priority based on context rules
    priority_config = approval_config.get("priority_rules", {})
    high_priority_threshold = priority_config.get("high_amount", 10000)

    if amount > high_priority_threshold or "variance_high" in flags or "compliance_fail" in flags:
        priority = "high"
    elif "compliance_warning" in flags:
        priority = "medium"
    else:
        priority = "normal"

    return {
        "approval_level": approval["level"],
        "approvers": approvers,
        "approver_count": len(approvers),
        "workflow_id": workflow_id,
        "sla_hours": approval["sla_hours"],
        "auto_approved": approval["auto_process"],
        "dual_approval_required": "dual_approval_required" in flags,
        "flags": flags,
        "gl_code": gl_code,
        "department": department["department"],
        "cost_center": department["cost_center"],
        "priority": priority,
        "context_driven": bool(context),
        "factory_id": "approval_route",
        "factory_version": "2.0.0",
    }


def handler(event, context):
    """Lambda entry point"""
    import asyncio
    return asyncio.run(approval_route(event))
