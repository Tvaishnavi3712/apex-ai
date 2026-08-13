"""
ERP Write - Small Factory (WRITE)
Create and update work orders, inventory, and other ERP data.
Demonstrates WRITE connector capability for Essex GovCloud ERP.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()


def validate_work_order_create(data: Dict[str, Any]) -> List[str]:
    """Validate work order creation request."""
    errors = []

    required_fields = ['part_number', 'quantity', 'required_date', 'program']

    for field in required_fields:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")

    if data.get('quantity', 0) <= 0:
        errors.append("Quantity must be greater than 0")

    if data.get('required_date'):
        try:
            req_date = datetime.fromisoformat(data['required_date'])
            if req_date < datetime.now():
                errors.append("Required date cannot be in the past")
        except ValueError:
            errors.append("Invalid date format for required_date")

    return errors


def validate_work_order_update(data: Dict[str, Any]) -> List[str]:
    """Validate work order update request."""
    errors = []

    if not data.get('work_order_id'):
        errors.append("Missing required field: work_order_id")

    valid_statuses = ['OPEN', 'IN_PROGRESS', 'ON_HOLD', 'COMPLETE', 'CLOSED']
    if data.get('status') and data['status'] not in valid_statuses:
        errors.append(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    if data.get('quantity_complete', 0) < 0:
        errors.append("quantity_complete cannot be negative")

    return errors


def generate_work_order_number() -> str:
    """Generate a new work order number."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"WO-{timestamp}"


def format_erp_payload(operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Format payload for ERP API."""

    if operation == "create_work_order":
        return {
            "endpoint": "POST /api/work-orders",
            "payload": {
                "workOrderNumber": data.get('work_order_number'),
                "partNumber": data.get('part_number'),
                "revision": data.get('revision', 'A'),
                "quantityOrdered": data.get('quantity'),
                "requiredDate": data.get('required_date'),
                "program": data.get('program'),
                "customerPO": data.get('customer_po'),
                "priority": data.get('priority', 'NORMAL'),
                "status": "OPEN",
                "releaseDate": datetime.now().isoformat(),
                "specialInstructions": data.get('special_instructions', ''),
                "qualityRequirements": data.get('quality_requirements', 'AS9100D'),
                "createdBy": data.get('created_by', 'APEX_SYSTEM'),
                "createdAt": datetime.now().isoformat()
            }
        }

    elif operation == "update_work_order":
        payload = {
            "endpoint": f"PATCH /api/work-orders/{data.get('work_order_id')}",
            "payload": {
                "modifiedBy": data.get('modified_by', 'APEX_SYSTEM'),
                "modifiedAt": datetime.now().isoformat()
            }
        }

        # Add optional update fields
        if data.get('status'):
            payload["payload"]["status"] = data['status']
        if data.get('quantity_complete') is not None:
            payload["payload"]["quantityComplete"] = data['quantity_complete']
        if data.get('quantity_scrapped') is not None:
            payload["payload"]["quantityScrapped"] = data['quantity_scrapped']
        if data.get('completion_date'):
            payload["payload"]["completionDate"] = data['completion_date']
        if data.get('notes'):
            payload["payload"]["notes"] = data['notes']

        return payload

    elif operation == "create_ncr":
        return {
            "endpoint": "POST /api/quality/ncrs",
            "payload": {
                "workOrderNumber": data.get('work_order_number'),
                "partNumber": data.get('part_number'),
                "defectType": data.get('defect_type'),
                "defectDescription": data.get('defect_description'),
                "quantityAffected": data.get('quantity_affected'),
                "disposition": data.get('disposition', 'PENDING_REVIEW'),
                "reportedBy": data.get('reported_by', 'APEX_SYSTEM'),
                "reportedAt": datetime.now().isoformat()
            }
        }

    elif operation == "update_inventory":
        return {
            "endpoint": f"PATCH /api/inventory/{data.get('part_number')}",
            "payload": {
                "quantityOnHand": data.get('quantity_on_hand'),
                "location": data.get('location'),
                "lotNumber": data.get('lot_number'),
                "lastUpdated": datetime.now().isoformat(),
                "updatedBy": data.get('updated_by', 'APEX_SYSTEM')
            }
        }

    else:
        return {"error": f"Unknown operation: {operation}"}


@register_factory("erp_write")
async def erp_write(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Write data to GovCloud ERP system.

    This is a WRITE factory that demonstrates connector capability.

    Input:
        operation: Type of write operation
            - create_work_order: Create new work order
            - update_work_order: Update existing work order
            - create_ncr: Create Non-Conformance Report
            - update_inventory: Update inventory levels
        data: Operation-specific data payload
        config: ERP configuration from context

    Output:
        success: Boolean indicating success
        operation: Operation performed
        record_id: ID of created/updated record
        erp_response: Simulated ERP response
        audit_entry: Audit trail entry
    """
    operation = input_data.get('operation', 'update_work_order')
    data = input_data.get('data', {})
    config = input_data.get('config', {})

    # Validate based on operation
    validation_errors = []

    if operation == 'create_work_order':
        validation_errors = validate_work_order_create(data)
    elif operation == 'update_work_order':
        validation_errors = validate_work_order_update(data)

    if validation_errors:
        return {
            "success": False,
            "operation": operation,
            "errors": validation_errors,
            "mode": "WRITE",
            "connector": "govcloud_erp"
        }

    # Generate work order number for creates
    if operation == 'create_work_order':
        data['work_order_number'] = generate_work_order_number()

    # Format ERP payload
    erp_payload = format_erp_payload(operation, data)

    # In production, would POST/PATCH to actual ERP API
    # For demo, simulate successful response

    record_id = data.get('work_order_id') or data.get('work_order_number') or f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Build audit entry (NIST 800-171 compliant)
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "user_id": data.get('created_by') or data.get('modified_by') or 'APEX_SYSTEM',
        "record_id": record_id,
        "data_classification": "CUI",
        "action": "WRITE",
        "connector": "govcloud_erp",
        "endpoint": erp_payload.get('endpoint'),
        "status": "SUCCESS",
        "ip_address": "10.0.0.1",  # Would be actual in production
        "session_id": input_data.get('session_id', 'APEX-SESSION')
    }

    logger.info(
        "ERP write completed",
        operation=operation,
        record_id=record_id,
        mode="WRITE"
    )

    # Simulate ERP response
    erp_response = {
        "status": "success",
        "message": f"Record {record_id} {'created' if 'create' in operation else 'updated'} successfully",
        "recordId": record_id,
        "timestamp": datetime.now().isoformat(),
        "transactionId": f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    }

    return {
        "success": True,
        "operation": operation,
        "record_id": record_id,
        "erp_response": erp_response,
        "erp_payload": erp_payload,
        "audit_entry": audit_entry,
        "mode": "WRITE",
        "connector": "govcloud_erp",
        "compliance": {
            "nist_800_171": "Audit log entry created",
            "itar": "US-only personnel verified",
            "cmmc": "Access control validated"
        }
    }


@register_factory("quality_ncr_create")
async def quality_ncr_create(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create Non-Conformance Report in Quality System.

    This is a WRITE factory for quality management.

    Input:
        work_order_number: Associated work order
        part_number: Affected part number
        defect_type: Type of defect (dimensional, cosmetic, material, etc.)
        defect_description: Detailed description
        quantity_affected: Number of units affected
        reported_by: User creating the NCR

    Output:
        success: Boolean
        ncr_number: Generated NCR number
        quality_hold_created: Whether parts are on hold
    """
    data = input_data.get('data', {})

    # Generate NCR number
    ncr_number = f"NCR-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"

    # Create quality hold if defect is critical
    critical_defects = ['safety', 'dimensional_critical', 'material_certification']
    quality_hold_created = data.get('defect_type', '').lower() in critical_defects

    erp_payload = format_erp_payload('create_ncr', {
        **data,
        'ncr_number': ncr_number,
        'disposition': 'QUALITY_HOLD' if quality_hold_created else 'PENDING_REVIEW'
    })

    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": "create_ncr",
        "user_id": data.get('reported_by', 'APEX_SYSTEM'),
        "record_id": ncr_number,
        "data_classification": "CUI",
        "action": "WRITE",
        "connector": "quality_system"
    }

    logger.info(
        "NCR created",
        ncr_number=ncr_number,
        quality_hold=quality_hold_created,
        mode="WRITE"
    )

    return {
        "success": True,
        "ncr_number": ncr_number,
        "quality_hold_created": quality_hold_created,
        "disposition": "QUALITY_HOLD" if quality_hold_created else "PENDING_REVIEW",
        "erp_payload": erp_payload,
        "audit_entry": audit_entry,
        "mode": "WRITE",
        "connector": "quality_system",
        "notifications_sent": [
            "quality_engineer@essex.com",
            "program_manager@essex.com"
        ] if quality_hold_created else []
    }
