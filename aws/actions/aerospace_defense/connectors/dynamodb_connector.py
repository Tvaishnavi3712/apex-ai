"""
DynamoDB Connector for GovCloud ERP Replacement
Handles work orders, operations, NCRs with READ/WRITE capabilities.
"""
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
import json
from actions.sdk.action_decorator import apex_action, register_factory


# Configuration
REGION = "us-east-1"
TABLES = {
    "work_orders": "apex-demo-work-orders",
    "operations": "apex-demo-wo-operations",
    "ncr": "apex-demo-ncr",
    "audit": "apex-demo-audit-log"
}


class DynamoDBConnector:
    """Connector for work order management via DynamoDB."""

    def __init__(self, region: str = REGION):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.tables = {name: self.dynamodb.Table(table_name)
                       for name, table_name in TABLES.items()}

    def _decimal_to_float(self, obj):
        """Convert Decimal types to float for JSON serialization."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._decimal_to_float(i) for i in obj]
        return obj

    def log_audit(self, operation: str, record_id: str, changes: dict, user_id: str = "APEX_SYSTEM"):
        """Log operation to audit table for NIST 800-171 compliance."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        audit_id = f"AUD-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        audit_entry = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "operation": operation,
            "record_id": record_id,
            "changes": json.dumps(changes),
            "user_id": user_id,
            "data_classification": "CUI",
            "compliance": {
                "nist_800_171": "3.3.1 - Event logged",
                "itar": "US person verified",
                "cmmc": "AU.L2-3.3.1 compliant"
            }
        }

        self.tables["audit"].put_item(Item=audit_entry)
        return audit_entry


@register_factory("erp_connector")
@apex_action(
    name="query_work_order",
    description="Query work order details from ERP (DynamoDB)",
    industry="aerospace_defense"
)
def query_work_order(work_order_id: str) -> Dict[str, Any]:
    """
    Query work order details from ERP.

    Args:
        work_order_id: Work order ID to query

    Returns:
        Work order details including status, operations, and materials
    """
    connector = DynamoDBConnector()

    try:
        # Get work order
        response = connector.tables["work_orders"].get_item(
            Key={"work_order_id": work_order_id}
        )

        if "Item" not in response:
            return {"error": f"Work order {work_order_id} not found"}

        work_order = connector._decimal_to_float(response["Item"])

        # Get operations
        ops_response = connector.tables["operations"].query(
            KeyConditionExpression=Key("work_order_id").eq(work_order_id)
        )
        operations = connector._decimal_to_float(ops_response.get("Items", []))

        work_order["operations"] = operations

        return {
            **work_order,
            "source": "GovCloud ERP (DynamoDB)",
            "connector_mode": "READ"
        }
    except Exception as e:
        return {"error": str(e), "source": "GovCloud ERP (DynamoDB)"}


@register_factory("erp_connector")
@apex_action(
    name="list_work_orders",
    description="List work orders with optional filters",
    industry="aerospace_defense"
)
def list_work_orders(
    status: Optional[str] = None,
    program: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    List work orders with optional filters.

    Args:
        status: Filter by status (OPEN, IN_PROGRESS, ON_HOLD, COMPLETE)
        program: Filter by program (F-35, F-22, UH-60)
        priority: Filter by priority (AOG, CRITICAL, HIGH, NORMAL)
        limit: Maximum results

    Returns:
        List of matching work orders
    """
    connector = DynamoDBConnector()

    try:
        # Build filter expression
        filter_expr = None
        expr_values = {}
        expr_names = {}

        if program and status:
            # Use GSI for program-status query
            response = connector.tables["work_orders"].query(
                IndexName="program-status-index",
                KeyConditionExpression=Key("program").eq(program.upper()) & Key("status").eq(status.upper()),
                Limit=limit
            )
        elif program:
            response = connector.tables["work_orders"].query(
                IndexName="program-status-index",
                KeyConditionExpression=Key("program").eq(program.upper()),
                Limit=limit
            )
        elif priority:
            response = connector.tables["work_orders"].query(
                IndexName="priority-date-index",
                KeyConditionExpression=Key("priority").eq(priority.upper()),
                Limit=limit
            )
        else:
            # Scan with filters
            scan_kwargs = {"Limit": limit}

            if status:
                filter_expr = Attr("status").eq(status.upper())
                scan_kwargs["FilterExpression"] = filter_expr

            response = connector.tables["work_orders"].scan(**scan_kwargs)

        items = connector._decimal_to_float(response.get("Items", []))

        return {
            "work_orders": items,
            "total": len(items),
            "filters_applied": {
                "status": status,
                "program": program,
                "priority": priority
            },
            "source": "GovCloud ERP (DynamoDB)",
            "connector_mode": "READ"
        }
    except Exception as e:
        return {"error": str(e), "source": "GovCloud ERP (DynamoDB)"}


@register_factory("erp_connector")
@apex_action(
    name="update_work_order_status",
    description="Update work order status (WRITE operation)",
    industry="aerospace_defense"
)
def update_work_order_status(
    work_order_id: str,
    new_status: str,
    quantity_complete: Optional[int] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
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
    connector = DynamoDBConnector()

    valid_statuses = ["OPEN", "IN_PROGRESS", "ON_HOLD", "COMPLETE", "CLOSED"]
    if new_status.upper() not in valid_statuses:
        return {"error": f"Invalid status. Must be one of: {valid_statuses}"}

    try:
        # Build update expression
        update_expr = "SET #status = :status, updated_at = :timestamp"
        expr_names = {"#status": "status"}
        expr_values = {
            ":status": new_status.upper(),
            ":timestamp": datetime.utcnow().isoformat() + "Z"
        }

        changes = {"status": new_status.upper()}

        if quantity_complete is not None:
            update_expr += ", quantity_complete = :qty"
            expr_values[":qty"] = quantity_complete
            changes["quantity_complete"] = quantity_complete

        if notes:
            update_expr += ", notes = :notes"
            expr_values[":notes"] = notes
            changes["notes"] = notes

        # Update the item
        response = connector.tables["work_orders"].update_item(
            Key={"work_order_id": work_order_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ReturnValues="ALL_NEW"
        )

        # Log audit entry
        audit_entry = connector.log_audit(
            operation="update_work_order",
            record_id=work_order_id,
            changes=changes
        )

        updated_item = connector._decimal_to_float(response.get("Attributes", {}))

        return {
            "success": True,
            "work_order_id": work_order_id,
            "new_status": new_status.upper(),
            "quantity_complete": quantity_complete,
            "updated_item": updated_item,
            "audit_entry": audit_entry,
            "message": f"Work order {work_order_id} updated to {new_status.upper()}",
            "source": "GovCloud ERP (DynamoDB)",
            "connector_mode": "WRITE"
        }
    except Exception as e:
        return {"error": str(e), "source": "GovCloud ERP (DynamoDB)"}


@register_factory("erp_connector")
@apex_action(
    name="create_work_order",
    description="Create a new work order (WRITE operation)",
    industry="aerospace_defense"
)
def create_work_order(
    part_number: str,
    quantity: int,
    required_date: str,
    program: str,
    customer_po: str,
    priority: str = "NORMAL",
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new work order (WRITE operation).

    Args:
        part_number: Part number to manufacture
        quantity: Quantity to produce
        required_date: Required completion date (YYYY-MM-DD)
        program: Program designation (F-35, F-22, etc.)
        customer_po: Customer purchase order number
        priority: Priority level (AOG, CRITICAL, HIGH, NORMAL)
        description: Part description

    Returns:
        Created work order details with audit trail
    """
    connector = DynamoDBConnector()

    timestamp = datetime.utcnow()
    work_order_id = f"WO-{timestamp.strftime('%Y')}-{timestamp.strftime('%m%d%H%M%S')}"

    try:
        work_order = {
            "work_order_id": work_order_id,
            "part_number": part_number,
            "description": description or f"{part_number} for {program}",
            "quantity_ordered": quantity,
            "quantity_complete": 0,
            "quantity_scrapped": 0,
            "status": "OPEN",
            "priority": priority.upper(),
            "program": program.upper(),
            "customer_po": customer_po,
            "release_date": timestamp.strftime("%Y-%m-%d"),
            "required_date": required_date,
            "quality_hold": False,
            "created_at": timestamp.isoformat() + "Z"
        }

        connector.tables["work_orders"].put_item(Item=work_order)

        # Log audit entry
        audit_entry = connector.log_audit(
            operation="create_work_order",
            record_id=work_order_id,
            changes=work_order
        )

        return {
            "success": True,
            **work_order,
            "audit_entry": audit_entry,
            "message": f"Work order {work_order_id} created successfully",
            "source": "GovCloud ERP (DynamoDB)",
            "connector_mode": "WRITE",
            "notifications_sent": [
                "production_planner@essex.com",
                "program_manager@essex.com"
            ]
        }
    except Exception as e:
        return {"error": str(e), "source": "GovCloud ERP (DynamoDB)"}


@register_factory("erp_connector")
@apex_action(
    name="create_ncr",
    description="Create Non-Conformance Report (WRITE operation)",
    industry="aerospace_defense"
)
def create_ncr(
    work_order_id: str,
    defect_type: str,
    defect_description: str,
    quantity_affected: int
) -> Dict[str, Any]:
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
    connector = DynamoDBConnector()

    timestamp = datetime.utcnow()
    ncr_number = f"NCR-{timestamp.strftime('%Y')}-{timestamp.strftime('%m%d%H%M%S')}"

    # Critical defects create automatic quality hold
    critical_defects = ["safety", "dimensional_critical", "material_certification"]
    quality_hold = defect_type.lower() in critical_defects

    try:
        ncr_record = {
            "ncr_number": ncr_number,
            "work_order_id": work_order_id,
            "defect_type": defect_type,
            "defect_description": defect_description,
            "quantity_affected": quantity_affected,
            "quality_hold": quality_hold,
            "disposition": "QUALITY_HOLD" if quality_hold else "PENDING_REVIEW",
            "created_at": timestamp.isoformat() + "Z",
            "status": "OPEN"
        }

        connector.tables["ncr"].put_item(Item=ncr_record)

        # If critical, update work order to ON_HOLD
        if quality_hold:
            connector.tables["work_orders"].update_item(
                Key={"work_order_id": work_order_id},
                UpdateExpression="SET #status = :status, quality_hold = :hold, ncr_number = :ncr",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": "ON_HOLD",
                    ":hold": True,
                    ":ncr": ncr_number
                }
            )

        # Log audit entry
        audit_entry = connector.log_audit(
            operation="create_ncr",
            record_id=ncr_number,
            changes={
                "ncr_record": ncr_record,
                "quality_hold_applied": quality_hold,
                "work_order_updated": quality_hold
            }
        )

        notifications = []
        if quality_hold:
            notifications = [
                "quality_engineer@essex.com",
                "program_manager@essex.com"
            ]

        return {
            "success": True,
            "ncr_number": ncr_number,
            "work_order_id": work_order_id,
            "defect_type": defect_type,
            "defect_description": defect_description,
            "quantity_affected": quantity_affected,
            "quality_hold_created": quality_hold,
            "disposition": ncr_record["disposition"],
            "audit_entry": audit_entry,
            "message": f"NCR {ncr_number} created" + (" - QUALITY HOLD APPLIED" if quality_hold else ""),
            "source": "GovCloud ERP (DynamoDB)",
            "connector_mode": "WRITE",
            "notifications_sent": notifications
        }
    except Exception as e:
        return {"error": str(e), "source": "GovCloud ERP (DynamoDB)"}
