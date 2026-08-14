"""
Action API endpoints
Manage actions for Foundry Agent Service
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
import uuid
from datetime import datetime

from models.action import Action, ActionCreate, ActionType, ActionCategory, ActionPack
from services.cosmos import CosmosService
from services.action_registry import get_registry, reload_registry, ActionRegistry
from core.config import settings

router = APIRouter()
db = CosmosService(settings.TABLE_ACTIONS)


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
                "bda_extract", "cosmos_db_lookup", "s3_read", "s3_write",
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
        ),
        ActionPack(
            name="Aerospace & Defense Pack",
            version="1.0",
            industry="aerospace_defense",
            description="Defense contract analysis, CNC programming assistance, work order management, and ITAR compliance for aerospace manufacturing",
            actions=[
                "contract_lookup", "pricing_history", "predict_pricing", "rfp_analysis",
                "generate_rfp_response", "generate_cost_breakdown", "cnc_review",
                "cnc_optimize", "workorder_query", "workorder_update", "ncr_create",
                "itar_compliance_check", "erp_read", "erp_write"
            ]
        ),
        # Nuclear Operations & Reliability — STP Phase 2 demo pack.
        # Powers the four use cases agreed with Prasad/Sabrina in March 2026:
        # policy lookup, equipment maintenance history, issue analysis, and
        # predictive maintenance — all backed by Foundry Agent Service + ApexSignal.
        ActionPack(
            name="Nuclear Operations & Reliability Pack",
            version="1.0",
            industry="nuclear_operations",
            description="Plant policy/procedure retrieval, equipment maintenance history queries, scanned work-package issue analysis, and predictive maintenance recommendations for nuclear power operations (STP Phase 2)",
            actions=[
                "policy_search", "policy_cite_extract",
                "oracle_pm_lookup", "engineer_attribution", "wp_attachment_fetch",
                "wp_corpus_search", "failure_mode_aggregate",
                "rul_predict", "anomaly_detect", "pm_recommend", "risk_score_compute",
                "intent_classify",
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

    # TODO: Register with Foundry Agent Service
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

    # TODO: Remove from Foundry Agent Service
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


@router.post("/registry/reload")
async def reload_action_registry():
    """
    Force a fresh discovery of all action handlers. Use this after
    updating handler files or the schema extractor — it clears the
    cached singleton so the next /registry/discover call returns
    freshly parsed schemas without a backend restart.
    """
    registry = reload_registry()
    return {
        "reloaded": True,
        "action_count": len(registry.get_all_actions()),
    }


@router.get("/registry/discover")
async def discover_actions(fresh: bool = False):
    """
    Discover all available actions from the action handlers.
    Scans the actions directory for all industry action handlers.
    Returns full metadata including input/output schemas.

    Pass ?fresh=true to force a rediscovery (useful after editing
    handler files without restarting the backend).
    """
    registry = reload_registry() if fresh else get_registry()
    all_actions = registry.get_all_actions()

    # Group by industry with schema info included (the lightweight
    # get_action_metadata() helper strips schemas; we need them here).
    by_industry: Dict[str, List[Dict[str, Any]]] = {}
    for action in all_actions:
        industry = action.industry
        if industry not in by_industry:
            by_industry[industry] = []
        by_industry[industry].append({
            "action_id": action.action_id,
            "name": action.name,
            "description": action.description,
            "category": action.category,
            "industry": action.industry,
            "handler_path": action.handler_path,
            "input_schema": action.input_schema or {},
            "output_schema": action.output_schema or {},
            "status": "available",
        })

    return {
        "total_actions": len(all_actions),
        "industries": list(by_industry.keys()),
        "actions_by_industry": by_industry,
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
async def register_all_actions(force_refresh: bool = True):
    """
    Register all discovered actions to the database.

    By default this rebuilds the registry from disk first (force_refresh=true)
    so freshly-edited handler files / new schemas land in Cosmos DB. Set
    ?force_refresh=false to skip the rediscovery step if you know the
    in-memory registry is already up-to-date.
    """
    registry = reload_registry() if force_refresh else get_registry()
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

            existing = await db.get_item({"action_id": action.action_id})
            if existing:
                # Preserve first-created-at + invocation_count but OVERWRITE
                # schema-bearing fields so stale empty schemas get corrected.
                action_data["created_at"] = existing.get("created_at", now.isoformat())
                if "invocation_count" in existing:
                    action_data["invocation_count"] = existing["invocation_count"]
                await db.put_item(action_data)
                registered.append(f"{action.action_id} (updated)")
            else:
                await db.put_item(action_data)
                registered.append(action.action_id)

        except Exception as e:
            errors.append({"action_id": action.action_id, "error": str(e)})

    return {
        "registered_count": len(registered),
        "registered_actions": registered,
        "errors": errors,
        "total_available": len(actions),
        "refreshed_from_disk": force_refresh,
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


@router.post("/seed-agentic-enterprise")
async def seed_agentic_enterprise_actions():
    """
    Seed all 11 Agentic Enterprise (66 Degrees vendor-neutral) actions
    into the Cosmos DB actions table.

    Why this exists:
        These actions don't have Lambda handler.py files (they're backed by
        the in-process simulator + Foundry Agent Service Strands tools), so the registry
        discover endpoint won't surface them. Seeding them directly into the
        DB makes them flow through the standard /api/v1/actions/ list →
        frontend gallery path, identical to insurance / aerospace actions.

    Three industries:
        supply_chain_orchestrator (4) — UC-1
        hospitality              (4) — UC-2
        commercial_real_estate   (3) — UC-3
    """
    now = datetime.utcnow()

    ae_actions = [
        # ─── UC-1 Supply Chain Orchestrator ───
        {
            "action_id": "supply_chain_orchestrator.check_inventory",
            "name": "check_inventory",
            "display_name": "Check Inventory",
            "description": "Look up SKU availability across all warehouses",
            "category": "agentic_orchestration",
            "industry": "supply_chain_orchestrator",
            "type": "lambda",
            "status": "active",
            "input_schema": {
                "sku": {"type": "string", "description": "SKU identifier (e.g. SKU-892)", "required": True},
            },
            "output_schema": {
                "sku":             {"type": "string", "description": "Echoed SKU"},
                "total_available": {"type": "number", "description": "Sum of available units across all warehouses"},
                "per_warehouse":   {"type": "array",  "description": "Per-warehouse breakdown"},
                "demand_forecast": {"type": "object", "description": "Campaign demand context for the SKU"},
            },
        },
        {
            "action_id": "supply_chain_orchestrator.find_alternative_supplier",
            "name": "find_alternative_supplier",
            "display_name": "Find Alternative Supplier",
            "description": "Rank approved suppliers and recommend the best fit",
            "category": "agentic_orchestration",
            "industry": "supply_chain_orchestrator",
            "type": "lambda",
            "status": "active",
            "input_schema": {
                "sku":                 {"type": "string", "description": "SKU to source", "required": True},
                "demand_window_days":  {"type": "number", "description": "Days available before campaign start", "required": False},
            },
            "output_schema": {
                "recommended": {"type": "object", "description": "Top supplier (lead_time_days, on_time_pct, defect_rate_ytd, unit_cost_usd)"},
                "alternates":  {"type": "array",  "description": "Up to 2 ranked alternates"},
            },
        },
        {
            "action_id": "supply_chain_orchestrator.draft_purchase_order",
            "name": "draft_purchase_order",
            "display_name": "Draft Purchase Order",
            "description": "Build a PO payload with totals and INCOTERMS",
            "category": "agentic_orchestration",
            "industry": "supply_chain_orchestrator",
            "type": "lambda",
            "status": "active",
            "input_schema": {
                "supplier_id":   {"type": "string", "description": "Approved supplier id", "required": True},
                "sku":           {"type": "string", "description": "SKU to order", "required": True},
                "quantity":      {"type": "number", "description": "Units to order", "required": True},
                "unit_cost_usd": {"type": "number", "description": "Per-unit cost", "required": True},
            },
            "output_schema": {
                "po_number":          {"type": "string", "description": "Generated PO number"},
                "total_usd":          {"type": "number", "description": "quantity × unit_cost_usd"},
                "requested_delivery": {"type": "string", "description": "ISO date the goods must arrive"},
                "status":             {"type": "string", "description": "Always 'DRAFT' — never auto-submitted"},
            },
        },
        {
            "action_id": "supply_chain_orchestrator.submit_for_approval",
            "name": "submit_for_approval",
            "display_name": "Submit for Approval",
            "description": "Route drafted PO to the human-review queue",
            "category": "agentic_orchestration",
            "industry": "supply_chain_orchestrator",
            "type": "lambda",
            "status": "active",
            "input_schema": {
                "po_number":   {"type": "string", "description": "PO number to route", "required": True},
                "total_usd":   {"type": "number", "description": "Total cost — drives severity tier", "required": True},
            },
            "output_schema": {
                "queue_id":  {"type": "string", "description": "Work-queue id"},
                "approver":  {"type": "string", "description": "Email of the human approver"},
                "severity":  {"type": "string", "description": "HIGH if > $25k, else NORMAL"},
                "sla_hours": {"type": "number", "description": "4 for HIGH, 24 for NORMAL"},
            },
        },
        # ─── UC-2 Cruise Concierge / Hospitality ───
        {
            "action_id": "hospitality.sentiment_score",
            "name": "sentiment_score",
            "display_name": "Sentiment Score",
            "description": "Score guest sentiment and recommend handoff if needed",
            "category": "customer_engagement",
            "industry": "hospitality",
            "type": "lambda",
            "status": "active",
            "input_schema": {
                "message": {"type": "string", "description": "Guest message text", "required": True},
            },
            "output_schema": {
                "score":               {"type": "number",  "description": "Normalized sentiment in [-1.0, +1.0]"},
                "label":               {"type": "string",  "description": "'positive' | 'neutral' | 'negative'"},
                "handoff_recommended": {"type": "boolean", "description": "True when frustration detected"},
            },
        },
        {
            "action_id": "hospitality.rag_faq_lookup",
            "name": "rag_faq_lookup",
            "display_name": "RAG FAQ Lookup",
            "description": "Retrieve the matching FAQ section verbatim",
            "category": "customer_engagement",
            "industry": "hospitality",
            "type": "lambda",
            "status": "active",
            "input_schema": {
                "query": {"type": "string", "description": "Guest question text", "required": True},
            },
            "output_schema": {
                "hit":   {"type": "boolean", "description": "True if any FAQ section matched"},
                "title": {"type": "string",  "description": "Matched section title (e.g. 'Pool Hours')"},
                "body":  {"type": "string",  "description": "Verbatim section body"},
            },
        },
        {
            "action_id": "hospitality.booking_modify",
            "name": "booking_modify",
            "display_name": "Booking Modify",
            "description": "Apply the date-change policy to a booking",
            "category": "customer_engagement",
            "industry": "hospitality",
            "type": "lambda",
            "status": "active",
            "input_schema": {
                "new_date": {"type": "string", "description": "New sail date in YYYY-MM-DD", "required": True},
            },
            "output_schema": {
                "booking_id":             {"type": "string", "description": "Booking reference"},
                "original_date":          {"type": "string", "description": "Original sail date"},
                "new_date":               {"type": "string", "description": "Staged new sail date"},
                "fee_usd":                {"type": "number", "description": "Date-change fee per policy"},
                "days_to_original_sail":  {"type": "number", "description": "Days from now to original sail"},
            },
        },
        {
            "action_id": "hospitality.agent_assist_handoff",
            "name": "agent_assist_handoff",
            "display_name": "Agent Assist Handoff",
            "description": "Hand off to human agent with context summary",
            "category": "customer_engagement",
            "industry": "hospitality",
            "type": "lambda",
            "status": "active",
            "input_schema": {},
            "output_schema": {
                "handoff":         {"type": "boolean", "description": "Always true"},
                "booking_summary": {"type": "object",  "description": "Booking + guest snapshot for the human agent"},
                "ts":              {"type": "string",  "description": "Handoff timestamp (ISO 8601)"},
            },
        },
        # ─── UC-3 Lease Extraction / CRE ───
        {
            "action_id": "commercial_real_estate.lease_extract",
            "name": "lease_extract",
            "display_name": "Lease Extract",
            "description": "Extract tenant, expiration, and liability terms",
            "category": "document_ai",
            "industry": "commercial_real_estate",
            "type": "lambda",
            "status": "active",
            "input_schema": {
                "text": {"type": "string", "description": "Raw lease text. Optional — defaults to bundled sample_lease.txt.", "required": False},
            },
            "output_schema": {
                "tenant_name":           {"type": "string", "description": "Legal tenant entity name"},
                "expiration_date":       {"type": "string", "description": "Lease expiration in ISO 8601"},
                "liability_clause_text": {"type": "string", "description": "Verbatim indemnification clause"},
                "confidence":            {"type": "object", "description": "Per-field confidence in [0.0, 1.0]"},
            },
        },
        {
            "action_id": "commercial_real_estate.lease_index",
            "name": "lease_index",
            "display_name": "Lease Index",
            "description": "Insert the extracted lease into the DuckDB table",
            "category": "document_ai",
            "industry": "commercial_real_estate",
            "type": "lambda",
            "status": "active",
            "input_schema": {
                "tenant_name":           {"type": "string", "description": "Tenant name to insert", "required": True},
                "expiration_date":       {"type": "string", "description": "ISO date", "required": True},
                "liability_clause_text": {"type": "string", "description": "Verbatim clause text", "required": True},
            },
            "output_schema": {
                "lease_id":        {"type": "string", "description": "Generated lease id (primary key)"},
                "table_row_count": {"type": "number", "description": "Total rows in leases after insert"},
            },
        },
        {
            "action_id": "commercial_real_estate.duckdb_query",
            "name": "duckdb_query",
            "display_name": "DuckDB Query",
            "description": "Run a SELECT query against the leases table",
            "category": "document_ai",
            "industry": "commercial_real_estate",
            "type": "lambda",
            "status": "active",
            "input_schema": {
                "sql": {"type": "string", "description": "SELECT statement against the leases table", "required": True},
            },
            "output_schema": {
                "columns": {"type": "array", "description": "Column names in order"},
                "rows":    {"type": "array", "description": "List of row arrays (parallel to columns)"},
            },
        },
    ]

    created = []
    updated = []
    errors = []

    for action_data in ae_actions:
        try:
            action_data["created_at"] = now.isoformat()
            action_data["updated_at"] = now.isoformat()
            action_data["version"] = "1.0"
            action_data["invocation_count"] = 0

            existing = await db.get_item({"action_id": action_data["action_id"]})
            if existing:
                action_data["created_at"] = existing.get("created_at", now.isoformat())
                # CAST to int — Cosmos DB returns numerics as Decimal, the
                # read-side convert_decimals helper turns them into Python
                # floats, and Cosmos DB rejects floats on write. Forcing int
                # here avoids the "Float types are not supported" error on
                # repeated seeds.
                action_data["invocation_count"] = int(existing.get("invocation_count", 0) or 0)
                updated.append(action_data["action_id"])
            else:
                created.append(action_data["action_id"])

            await db.put_item(action_data)
        except Exception as e:
            errors.append({"action_id": action_data["action_id"], "error": str(e)})

    return {
        "message": f"Seeded {len(created) + len(updated)} Agentic Enterprise actions",
        "created": created,
        "updated": updated,
        "errors": errors if errors else None,
    }


@router.post("/registry/invoke/{action_id}")
async def invoke_registered_action(action_id: str, payload: dict):
    """
    Invoke a registered action handler directly. Used by the Test Runner
    tab. Returns a structured envelope (see ActionRegistry.invoke_action_async)
    so the UI can render success / error / timing without ambiguity.
    """
    registry = get_registry()

    if not registry.get_action(action_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action {action_id} not found in registry",
        )

    envelope = await registry.invoke_action_async(action_id, payload or {})

    return {
        "action_id": action_id,
        "status": "success" if envelope.get("ok") else "error",
        "ok": envelope.get("ok"),
        "result": envelope.get("result"),
        "error": envelope.get("error"),
        "error_type": envelope.get("error_type"),
        "traceback": envelope.get("traceback"),
        "duration_ms": envelope.get("duration_ms"),
    }
