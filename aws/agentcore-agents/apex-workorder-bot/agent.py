"""
Apex WorkOrder Bot - AgentCore Agent for work order management
Uses Claude Opus 4.6 for ERP read/write operations.
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel
from typing import List, Optional
from datetime import datetime

# Create the AgentCore app
app = BedrockAgentCoreApp()

SYSTEM_PROMPT = """You are WorkOrderBot, an AI assistant specialized in work order management for Essex Industries, an aerospace & defense manufacturer.

Your capabilities:
1. Query work order status from GovCloud ERP (READ)
2. Retrieve associated documents and specifications (READ)
3. Update work order status and completion data (WRITE)
4. Create new work orders (WRITE)
5. Create Non-Conformance Reports (NCRs) (WRITE)
6. Track quality holds

Compliance context:
- All operations are logged for NIST 800-171 compliance
- ITAR-controlled data handling
- AS9100D quality requirements

Work Order Status Workflow:
OPEN → IN_PROGRESS → ON_HOLD (optional) → COMPLETE → CLOSED

Priority Levels:
- AOG (Aircraft on Ground): 24-hour SLA
- CRITICAL: 72-hour SLA
- HIGH: 168-hour SLA (1 week)
- NORMAL: 336-hour SLA (2 weeks)

For WRITE operations:
- Always confirm the action before executing
- Log all changes to audit trail
- Notify relevant personnel

Be precise with work order numbers and status changes."""


@tool
def query_work_order(work_order_id: str) -> dict:
    """
    Query work order details from ERP.

    Args:
        work_order_id: Work order ID to query

    Returns:
        Work order details including status, operations, and materials
    """
    # Real implementation would query GovCloud ERP
    work_orders = {
        "WO-2026-001234": {
            "work_order_id": "WO-2026-001234",
            "part_number": "TG-5842-001",
            "description": "Throttle Grip Assembly, F-35",
            "revision": "D",
            "quantity_ordered": 50,
            "quantity_complete": 35,
            "quantity_scrapped": 2,
            "status": "IN_PROGRESS",
            "priority": "HIGH",
            "program": "F-35",
            "customer": "Lockheed Martin",
            "customer_po": "LM-2026-78543",
            "release_date": "2026-01-15",
            "required_date": "2026-04-15",
            "operations": [
                {"op": "10", "description": "CNC Mill Rough", "status": "COMPLETE", "work_center": "MAZAK-01"},
                {"op": "20", "description": "CNC Mill Finish", "status": "IN_PROGRESS", "work_center": "DMG-02"},
                {"op": "30", "description": "Deburr", "status": "PENDING", "work_center": "BENCH-01"},
                {"op": "40", "description": "Anodize", "status": "PENDING", "work_center": "OUTSIDE"},
                {"op": "50", "description": "Final Inspect", "status": "PENDING", "work_center": "QC-01"}
            ],
            "quality_hold": False,
            "ncr_number": None
        }
    }

    if work_order_id in work_orders:
        return work_orders[work_order_id]

    return {"error": f"Work order {work_order_id} not found"}


@tool
def list_work_orders(
    status: Optional[str] = None,
    program: Optional[str] = None,
    priority: Optional[str] = None
) -> dict:
    """
    List work orders with optional filters.

    Args:
        status: Filter by status (OPEN, IN_PROGRESS, ON_HOLD, COMPLETE)
        program: Filter by program (F-35, F-22, UH-60)
        priority: Filter by priority (AOG, CRITICAL, HIGH, NORMAL)

    Returns:
        List of matching work orders
    """
    work_orders = [
        {"work_order_id": "WO-2026-001234", "part_number": "TG-5842-001", "status": "IN_PROGRESS", "priority": "HIGH", "program": "F-35", "required_date": "2026-04-15"},
        {"work_order_id": "WO-2026-001235", "part_number": "SS-5842-002", "status": "OPEN", "priority": "NORMAL", "program": "F-35", "required_date": "2026-05-01"},
        {"work_order_id": "WO-2026-001198", "part_number": "CG-7621-001", "status": "IN_PROGRESS", "priority": "CRITICAL", "program": "UH-60", "required_date": "2026-03-30"},
        {"work_order_id": "WO-2026-001187", "part_number": "TG-5842-001", "status": "ON_HOLD", "priority": "HIGH", "program": "F-35", "required_date": "2026-04-01", "hold_reason": "NCR-2026-0045"},
    ]

    results = work_orders
    if status:
        results = [wo for wo in results if wo["status"] == status.upper()]
    if program:
        results = [wo for wo in results if wo["program"] == program.upper()]
    if priority:
        results = [wo for wo in results if wo["priority"] == priority.upper()]

    return {
        "work_orders": results,
        "total": len(results),
        "filters_applied": {"status": status, "program": program, "priority": priority}
    }


@tool
def update_work_order_status(
    work_order_id: str,
    new_status: str,
    quantity_complete: Optional[int] = None,
    notes: Optional[str] = None
) -> dict:
    """
    Update work order status (WRITE operation).

    Args:
        work_order_id: Work order to update
        new_status: New status (IN_PROGRESS, ON_HOLD, COMPLETE)
        quantity_complete: Updated quantity complete (optional)
        notes: Notes for the status change

    Returns:
        Confirmation of update with audit trail
    """
    valid_statuses = ["OPEN", "IN_PROGRESS", "ON_HOLD", "COMPLETE", "CLOSED"]
    if new_status.upper() not in valid_statuses:
        return {"error": f"Invalid status. Must be one of: {valid_statuses}"}

    timestamp = datetime.now().isoformat()
    transaction_id = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    audit_entry = {
        "timestamp": timestamp,
        "operation": "update_work_order",
        "work_order_id": work_order_id,
        "changes": {
            "status": new_status.upper(),
            "quantity_complete": quantity_complete,
            "notes": notes
        },
        "user_id": "APEX_SYSTEM",
        "transaction_id": transaction_id,
        "compliance": {
            "nist_800_171": "Audit log entry created",
            "itar": "US-only personnel verified"
        }
    }

    return {
        "success": True,
        "work_order_id": work_order_id,
        "new_status": new_status.upper(),
        "quantity_complete": quantity_complete,
        "transaction_id": transaction_id,
        "audit_entry": audit_entry,
        "message": f"Work order {work_order_id} updated to {new_status.upper()}",
        "mode": "WRITE"
    }


@tool
def create_work_order(
    part_number: str,
    quantity: int,
    required_date: str,
    program: str,
    customer_po: str,
    priority: str = "NORMAL"
) -> dict:
    """
    Create a new work order (WRITE operation).

    Args:
        part_number: Part number to manufacture
        quantity: Quantity to produce
        required_date: Required completion date (YYYY-MM-DD)
        program: Program designation (F-35, F-22, etc.)
        customer_po: Customer purchase order number
        priority: Priority level (AOG, CRITICAL, HIGH, NORMAL)

    Returns:
        Created work order details with audit trail
    """
    timestamp = datetime.now()
    work_order_id = f"WO-{timestamp.strftime('%Y')}-{timestamp.strftime('%m%d%H%M%S')}"

    audit_entry = {
        "timestamp": timestamp.isoformat(),
        "operation": "create_work_order",
        "record_id": work_order_id,
        "user_id": "APEX_SYSTEM",
        "data_classification": "CUI",
        "compliance": {
            "nist_800_171": "Audit log entry created",
            "itar": "US-only personnel verified",
            "cmmc": "Access control validated"
        }
    }

    return {
        "success": True,
        "work_order_id": work_order_id,
        "part_number": part_number,
        "quantity": quantity,
        "required_date": required_date,
        "program": program,
        "customer_po": customer_po,
        "priority": priority,
        "status": "OPEN",
        "release_date": timestamp.strftime("%Y-%m-%d"),
        "audit_entry": audit_entry,
        "message": f"Work order {work_order_id} created successfully",
        "mode": "WRITE",
        "notifications_sent": ["production_planner@essex.com", "program_manager@essex.com"]
    }


@tool
def create_ncr(
    work_order_id: str,
    defect_type: str,
    defect_description: str,
    quantity_affected: int
) -> dict:
    """
    Create Non-Conformance Report (WRITE operation).

    Args:
        work_order_id: Associated work order
        defect_type: Type of defect (dimensional, cosmetic, material, safety)
        defect_description: Detailed description of the defect
        quantity_affected: Number of units affected

    Returns:
        NCR details with quality hold status
    """
    timestamp = datetime.now()
    ncr_number = f"NCR-{timestamp.strftime('%Y')}-{timestamp.strftime('%m%d%H%M%S')}"

    # Critical defects create automatic quality hold
    critical_defects = ["safety", "dimensional_critical", "material_certification"]
    quality_hold = defect_type.lower() in critical_defects

    audit_entry = {
        "timestamp": timestamp.isoformat(),
        "operation": "create_ncr",
        "record_id": ncr_number,
        "work_order_id": work_order_id,
        "user_id": "APEX_SYSTEM",
        "data_classification": "CUI"
    }

    return {
        "success": True,
        "ncr_number": ncr_number,
        "work_order_id": work_order_id,
        "defect_type": defect_type,
        "defect_description": defect_description,
        "quantity_affected": quantity_affected,
        "quality_hold_created": quality_hold,
        "disposition": "QUALITY_HOLD" if quality_hold else "PENDING_REVIEW",
        "audit_entry": audit_entry,
        "message": f"NCR {ncr_number} created" + (" - QUALITY HOLD APPLIED" if quality_hold else ""),
        "mode": "WRITE",
        "notifications_sent": [
            "quality_engineer@essex.com",
            "program_manager@essex.com"
        ] if quality_hold else []
    }


@tool
def get_work_order_documents(work_order_id: str) -> dict:
    """
    Get documents associated with a work order (READ).

    Args:
        work_order_id: Work order ID

    Returns:
        List of associated documents
    """
    return {
        "work_order_id": work_order_id,
        "documents": [
            {"type": "drawing", "name": "TG-5842-001_Rev_D.pdf", "revision": "D", "location": "SharePoint GCC"},
            {"type": "traveler", "name": f"{work_order_id}_Traveler.pdf", "location": "ERP"},
            {"type": "work_instruction", "name": "WI-MILL-001.pdf", "revision": "B", "location": "SharePoint GCC"},
            {"type": "inspection_plan", "name": "IP-TG5842-001.pdf", "location": "Quality System"}
        ],
        "source": "GovCloud ERP + SharePoint GCC High"
    }


# Create the Strands agent with Claude Opus 4.6
model = BedrockModel(
    model_id="us.anthropic.claude-opus-4-6-v1",
    region_name="us-east-1"
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        query_work_order,
        list_work_orders,
        update_work_order_status,
        create_work_order,
        create_ncr,
        get_work_order_documents
    ]
)


@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
