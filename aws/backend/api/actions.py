"""
Action API endpoints
Manage actions for AgentCore Gateway
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
import uuid
from datetime import datetime

from models.action import Action, ActionCreate, ActionType, ActionCategory, ActionPack
from services.dynamodb import DynamoDBService
from services.action_registry import get_registry, ActionRegistry
from core.config import settings

router = APIRouter()
db = DynamoDBService(settings.DYNAMODB_ACTIONS)


@router.get("/", response_model=List[Action])
async def list_actions(
    category: Optional[ActionCategory] = Query(None),
    type: Optional[ActionType] = Query(None),
    industry: Optional[str] = Query(None),
    limit: int = Query(100, le=500)
):
    """List all actions with optional filters"""
    filters = {}
    if category:
        filters["category"] = category.value
    if type:
        filters["type"] = type.value
    if industry:
        filters["industry"] = industry

    items = await db.scan(filters=filters, limit=limit)
    return [Action(**item) for item in items]


@router.get("/gallery")
async def get_action_gallery():
    """Get actions organized by category for the gallery UI"""
    all_actions = await db.scan(limit=500)

    gallery = {}
    for action in all_actions:
        category = action.get("category", "other")
        if category not in gallery:
            gallery[category] = []
        gallery[category].append(Action(**action))

    return gallery


@router.get("/packs")
async def list_action_packs():
    """List all action packs (industry bundles)"""
    # Pre-defined packs
    packs = [
        ActionPack(
            name="Financial Services Pack",
            version="1.0",
            industry="financial_services",
            description="Pre-built actions for invoice processing, PO matching, vendor validation, and approval routing",
            actions=[
                "bda_extract", "vendor_lookup", "po_match", "approval_route",
                "compliance_check", "create_task", "send_notification"
            ]
        ),
        ActionPack(
            name="Core Actions Pack",
            version="1.0",
            industry="general",
            description="Universal actions for document processing, data lookup, and notifications",
            actions=[
                "bda_extract", "dynamodb_lookup", "s3_read", "s3_write",
                "send_email", "send_slack", "human_review"
            ]
        ),
        ActionPack(
            name="Healthcare Payers Pack",
            version="1.0",
            industry="healthcare_payers",
            description="Claims processing, eligibility verification, medical necessity review, and fraud detection",
            actions=[
                "claims_adjudication", "eligibility_verify", "medical_necessity",
                "payment_calculate", "fraud_detection"
            ]
        ),
        ActionPack(
            name="Healthcare Providers Pack",
            version="1.0",
            industry="healthcare_providers",
            description="Patient management, insurance verification, referrals, and EHR updates",
            actions=[
                "patient_lookup", "insurance_verify", "referral_validate",
                "appointment_schedule", "ehr_update"
            ]
        ),
        ActionPack(
            name="Healthcare Clinical Pack",
            version="1.0",
            industry="healthcare_clinical",
            description="Lab validation, critical alerts, drug interactions, and clinical decision support",
            actions=[
                "lab_validate", "critical_value_alert", "drug_interaction",
                "formulary_check", "clinical_decision"
            ]
        ),
        ActionPack(
            name="Retail Pack",
            version="1.0",
            industry="retail",
            description="Receipt validation, return processing, fraud scoring, and refunds",
            actions=[
                "receipt_validate", "return_policy", "fraud_score",
                "inventory_update", "refund_process"
            ]
        ),
        ActionPack(
            name="CPG Pack",
            version="1.0",
            industry="cpg",
            description="Ingredient validation, regulatory compliance, label review, and allergen detection",
            actions=[
                "ingredient_validate", "regulatory_check", "label_compliance",
                "nutrition_validate", "allergen_check"
            ]
        ),
        ActionPack(
            name="Insurance Underwriting Pack",
            version="1.0",
            industry="insurance_underwriting",
            description="Risk scoring, premium calculation, coverage validation, and auto-decisioning",
            actions=[
                "risk_score", "premium_calculate", "coverage_validate",
                "loss_history", "auto_decision"
            ]
        ),
        ActionPack(
            name="Contact Center Pack",
            version="1.0",
            industry="contact_center",
            description="Sentiment analysis, compliance checking, quality scoring, and escalation detection",
            actions=[
                "sentiment_analyze", "compliance_check", "quality_score",
                "coaching_recommend", "escalation_detect"
            ]
        ),
        ActionPack(
            name="Airlines Pack",
            version="1.0",
            industry="airlines",
            description="Passenger management, rebooking, hotel booking, EU261 compensation, and baggage tracing",
            actions=[
                "affected_passengers", "auto_rebook", "hotel_booking",
                "eu261_compensation", "baggage_trace"
            ]
        ),
        ActionPack(
            name="Supply Chain Pack",
            version="1.0",
            industry="supply_chain",
            description="Demand forecasting, inventory analysis, EOQ calculation, and supplier scorecards",
            actions=[
                "forecast_analyze", "inventory_analyze", "eoq_calculate",
                "reorder_point", "quality_metrics", "delivery_metrics", "scorecard_generate"
            ]
        ),
        ActionPack(
            name="Manufacturing Pack",
            version="1.0",
            industry="manufacturing",
            description="Inventory management, carrier validation, and quality threshold checking",
            actions=[
                "inventory_lookup", "carrier_validation", "quality_threshold"
            ]
        ),
        ActionPack(
            name="HR Pack",
            version="1.0",
            industry="hr",
            description="Job matching, compensation validation, and background check initiation",
            actions=[
                "job_requirement_match", "compensation_validation", "background_check"
            ]
        ),
        ActionPack(
            name="Integrations Pack",
            version="1.0",
            industry="integrations",
            description="External system integrations for Slack notifications, Teams bot, email intake, and ServiceNow",
            actions=[
                "slack_notify", "teams_bot", "email_intake", "servicenow"
            ]
        )
    ]

    return packs


@router.get("/{action_id}", response_model=Action)
async def get_action(action_id: str):
    """Get a specific action by ID"""
    item = await db.get_item({"action_id": action_id})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action {action_id} not found"
        )
    return Action(**item)


@router.post("/", response_model=Action, status_code=status.HTTP_201_CREATED)
async def create_action(action: ActionCreate):
    """Create a new action"""
    action_id = action.name  # Use name as ID for simplicity
    now = datetime.utcnow()

    # Check if action already exists
    existing = await db.get_item({"action_id": action_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Action {action_id} already exists"
        )

    action_data = action.model_dump()
    action_data.update({
        "action_id": action_id,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "status": "active"
    })

    await db.put_item(action_data)

    # TODO: Register with AgentCore Gateway
    # 1. If Lambda, add Lambda target to Gateway
    # 2. If OpenAPI, add API target to Gateway
    # 3. Store gateway_target_id

    return Action(**action_data)


@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action(action_id: str):
    """Delete an action"""
    existing = await db.get_item({"action_id": action_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action {action_id} not found"
        )

    # TODO: Remove from AgentCore Gateway
    await db.delete_item({"action_id": action_id})


@router.post("/{action_id}/test")
async def test_action(action_id: str, input: dict):
    """Test an action with sample input"""
    action = await get_action(action_id)

    # TODO: Invoke the action directly
    # 1. If Lambda, invoke Lambda
    # 2. If Gateway, call through Gateway

    return {
        "action_id": action_id,
        "status": "testing",
        "input": input
    }


@router.post("/deploy-pack/{pack_name}")
async def deploy_action_pack(pack_name: str):
    """Deploy all actions in a pack to Gateway"""
    packs = await list_action_packs()
    pack = next((p for p in packs if p.name == pack_name), None)

    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pack {pack_name} not found"
        )

    # TODO: Deploy all actions in the pack

    return {
        "pack": pack_name,
        "status": "deploying",
        "actions": pack.actions
    }


@router.get("/registry/discover")
async def discover_actions():
    """
    Discover all available actions from the action handlers.
    Scans the actions directory for all industry action handlers.
    """
    registry = get_registry()
    actions = registry.get_action_metadata()

    # Group by industry
    by_industry = {}
    for action in actions:
        industry = action["industry"]
        if industry not in by_industry:
            by_industry[industry] = []
        by_industry[industry].append(action)

    return {
        "total_actions": len(actions),
        "industries": list(by_industry.keys()),
        "actions_by_industry": by_industry
    }


@router.get("/registry/industry/{industry}")
async def get_industry_actions(industry: str):
    """Get all actions for a specific industry"""
    registry = get_registry()
    actions = registry.get_actions_by_industry(industry)

    if not actions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No actions found for industry: {industry}"
        )

    return {
        "industry": industry,
        "action_count": len(actions),
        "actions": [
            {
                "action_id": a.action_id,
                "name": a.name,
                "description": a.description,
                "category": a.category,
            }
            for a in actions
        ]
    }


@router.post("/registry/register-all")
async def register_all_actions():
    """
    Register all discovered actions to the database.
    This creates action records for all industry handlers.
    """
    registry = get_registry()
    actions = registry.get_all_actions()
    now = datetime.utcnow()

    registered = []
    errors = []

    for action in actions:
        try:
            action_data = {
                "action_id": action.action_id,
                "name": action.name,
                "description": action.description,
                "category": action.category,
                "industry": action.industry,
                "type": "lambda",
                "status": "active",
                "handler_path": action.handler_path,
                "input_schema": action.input_schema or {},
                "output_schema": action.output_schema or {},
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }

            # Check if exists first
            existing = await db.get_item({"action_id": action.action_id})
            if not existing:
                await db.put_item(action_data)
                registered.append(action.action_id)
            else:
                # Update existing
                action_data["created_at"] = existing.get("created_at", now.isoformat())
                await db.put_item(action_data)
                registered.append(f"{action.action_id} (updated)")

        except Exception as e:
            errors.append({"action_id": action.action_id, "error": str(e)})

    return {
        "registered_count": len(registered),
        "registered_actions": registered,
        "errors": errors,
        "total_available": len(actions)
    }


@router.post("/seed-insurance")
async def seed_insurance_actions():
    """
    Seed all insurance underwriting actions including CRE-specific ones.
    """
    now = datetime.utcnow()

    insurance_actions = [
        # General Insurance Underwriting
        {
            "action_id": "insurance.application_extract",
            "name": "application_extract",
            "display_name": "Application Extract",
            "description": "Extract data from insurance application documents",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"document_id": {"type": "string"}, "blueprint_id": {"type": "string"}},
            "output_schema": {"applicant_name": {"type": "string"}, "policy_type": {"type": "string"}},
        },
        {
            "action_id": "insurance.credit_check",
            "name": "credit_check",
            "display_name": "Credit Check",
            "description": "Run credit score check for applicant",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"applicant_id": {"type": "string"}, "ssn": {"type": "string"}},
            "output_schema": {"credit_score": {"type": "number"}, "credit_tier": {"type": "string"}},
        },
        {
            "action_id": "insurance.loss_history_check",
            "name": "loss_history_check",
            "display_name": "Loss History Check",
            "description": "Check loss history from carrier records",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"applicant_id": {"type": "string"}},
            "output_schema": {"total_claims": {"type": "number"}, "loss_ratio": {"type": "number"}},
        },
        {
            "action_id": "insurance.risk_score",
            "name": "risk_score",
            "display_name": "Risk Score",
            "description": "Calculate risk score based on application data",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"application_data": {"type": "object"}},
            "output_schema": {"risk_score": {"type": "number"}, "risk_tier": {"type": "string"}},
        },
        {
            "action_id": "insurance.premium_calculate",
            "name": "premium_calculate",
            "display_name": "Premium Calculate",
            "description": "Calculate premium based on risk and coverage",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"risk_score": {"type": "number"}, "coverage_amount": {"type": "number"}},
            "output_schema": {"base_premium": {"type": "number"}, "final_premium": {"type": "number"}},
        },
        {
            "action_id": "insurance.underwriter_route",
            "name": "underwriter_route",
            "display_name": "Underwriter Route",
            "description": "Route to appropriate underwriter based on risk",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"risk_score": {"type": "number"}, "tiv": {"type": "number"}},
            "output_schema": {"assigned_underwriter": {"type": "string"}, "priority": {"type": "string"}},
        },
        # CRE-Specific Actions
        {
            "action_id": "cre.document_extract",
            "name": "cre_document_extract",
            "display_name": "CRE Document Extract",
            "description": "Extract property and submission data from CRE documents using BDA blueprint",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"document_id": {"type": "string"}, "blueprint": {"type": "string"}},
            "output_schema": {"property_name": {"type": "string"}, "property_type": {"type": "string"}, "tiv": {"type": "number"}, "location": {"type": "object"}},
        },
        {
            "action_id": "cre.risk_score",
            "name": "cre_risk_score",
            "display_name": "CRE Risk Score",
            "description": "Calculate risk score based on CRE property factors",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"property_data": {"type": "object"}, "loss_history": {"type": "object"}},
            "output_schema": {"risk_score": {"type": "number"}, "risk_tier": {"type": "string"}, "risk_factors": {"type": "array"}},
        },
        {
            "action_id": "cre.premium_calculate",
            "name": "cre_premium_calculate",
            "display_name": "CRE Premium Calculate",
            "description": "Calculate CRE premium using rate tables and risk adjustments",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"tiv": {"type": "number"}, "risk_score": {"type": "number"}, "property_type": {"type": "string"}},
            "output_schema": {"base_premium": {"type": "number"}, "final_premium": {"type": "number"}, "rate_per_100": {"type": "number"}},
        },
        {
            "action_id": "cre.loss_history",
            "name": "cre_loss_history",
            "display_name": "CRE Loss History",
            "description": "Retrieve and analyze loss history from carrier records",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"account_id": {"type": "string"}, "years": {"type": "number"}},
            "output_schema": {"total_claims": {"type": "number"}, "total_paid": {"type": "number"}, "loss_ratio": {"type": "number"}},
        },
        {
            "action_id": "cre.auto_decision",
            "name": "cre_auto_decision",
            "display_name": "CRE Auto Decision",
            "description": "Apply underwriting rules to make CRE decision",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"risk_score": {"type": "number"}, "tiv": {"type": "number"}, "loss_ratio": {"type": "number"}},
            "output_schema": {"decision": {"type": "string"}, "confidence": {"type": "number"}, "reasons": {"type": "array"}},
        },
        {
            "action_id": "cre.cat_model",
            "name": "cre_cat_model",
            "display_name": "CRE CAT Model",
            "description": "Run catastrophe modeling for CAT-exposed properties",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"location": {"type": "object"}, "tiv": {"type": "number"}},
            "output_schema": {"hurricane_pml": {"type": "number"}, "earthquake_pml": {"type": "number"}, "flood_zone": {"type": "string"}},
        },
        {
            "action_id": "cre.generate_referral",
            "name": "cre_generate_referral",
            "display_name": "CRE Generate Referral",
            "description": "Generate referral package for human underwriter review",
            "category": "insurance_underwriting",
            "industry": "insurance_underwriting",
            "type": "lambda",
            "status": "active",
            "input_schema": {"submission_data": {"type": "object"}, "risk_assessment": {"type": "object"}},
            "output_schema": {"referral_package": {"type": "object"}, "recommended_approver": {"type": "string"}},
        },
    ]

    created = []
    updated = []
    errors = []

    for action_data in insurance_actions:
        try:
            action_data["created_at"] = now.isoformat()
            action_data["updated_at"] = now.isoformat()
            action_data["version"] = "1.0"
            action_data["invocation_count"] = 0

            existing = await db.get_item({"action_id": action_data["action_id"]})
            if existing:
                action_data["created_at"] = existing.get("created_at", now.isoformat())
                action_data["invocation_count"] = existing.get("invocation_count", 0)
                updated.append(action_data["action_id"])
            else:
                created.append(action_data["action_id"])

            await db.put_item(action_data)

        except Exception as e:
            errors.append({"action_id": action_data["action_id"], "error": str(e)})

    return {
        "message": f"Seeded {len(created) + len(updated)} insurance underwriting actions",
        "created": created,
        "updated": updated,
        "errors": errors if errors else None
    }


@router.post("/registry/invoke/{action_id}")
async def invoke_registered_action(action_id: str, payload: dict):
    """
    Invoke a registered action handler directly.
    This is for testing and development purposes.
    """
    registry = get_registry()
    action = registry.get_action(action_id)

    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action {action_id} not found in registry"
        )

    result = registry.invoke_action(action_id, **payload)

    return {
        "action_id": action_id,
        "status": "error" if "error" in result else "success",
        "result": result
    }
