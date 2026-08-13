"""
Action Registry Service
Discovers and manages all action handlers across industries
"""
import asyncio
import inspect
import os
import sys
import time
import traceback
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .action_schema_extractor import extract_schemas


@dataclass
class RegisteredAction:
    """Represents a registered action"""
    action_id: str
    name: str
    description: str
    category: str
    industry: str
    handler_path: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    handler_function: Optional[callable] = None
    class_handler: Optional[type] = None


class ActionRegistry:
    """
    Registry for all action handlers in the system.
    Discovers actions from the actions directory structure.
    """

    # Define all industries with their actions
    INDUSTRY_ACTIONS = {
        "healthcare_payers": [
            "claims_adjudication",
            "eligibility_verify",
            "medical_necessity",
            "payment_calculate",
            "fraud_detection",
        ],
        "healthcare_providers": [
            "patient_lookup",
            "insurance_verify",
            "referral_validate",
            "appointment_schedule",
            "ehr_update",
        ],
        "healthcare_clinical": [
            "lab_validate",
            "critical_value_alert",
            "drug_interaction",
            "formulary_check",
            "clinical_decision",
        ],
        "retail": [
            "receipt_validate",
            "return_policy",
            "fraud_score",
            "inventory_update",
            "refund_process",
        ],
        "cpg": [
            "ingredient_validate",
            "regulatory_check",
            "label_compliance",
            "nutrition_validate",
            "allergen_check",
        ],
        "insurance_underwriting": [
            # General underwriting actions
            "application_extract",
            "credit_check",
            "loss_history_check",
            "risk_score",
            "premium_calculate",
            "underwriter_route",
            # CRE-specific actions
            "document_extract",
            "cre_risk_score",
            "cre_premium_calculate",
            "cre_loss_history",
            "auto_decision",
            "cat_model",
            "generate_referral",
            "coverage_validate",
        ],
        "contact_center": [
            "sentiment_analyze",
            "compliance_check",
            "quality_score",
            "coaching_recommend",
            "escalation_detect",
        ],
        "airlines": [
            "affected_passengers",
            "auto_rebook",
            "hotel_booking",
            "eu261_compensation",
            "baggage_trace",
        ],
        "supply_chain": [
            "forecast_analyze",
            "inventory_analyze",
            "eoq_calculate",
            "reorder_point",
            "quality_metrics",
            "delivery_metrics",
            "scorecard_generate",
        ],
        "manufacturing": [
            "inventory_lookup",
            "carrier_validation",
            "quality_threshold",
        ],
        "hr": [
            "job_requirement_match",
            "compensation_validation",
            "background_check",
        ],
        "financial_services": [
            "vendor_lookup",
            "po_match",
            "approval_route",
            "compliance_check",
            "human_review",
        ],
        "core": [
            "bda_extract",
            "cosmos_db_lookup",
            "s3_operations",
            "notification",
            # JIRA Cloud integration — used by Telecommunications cycle pipeline
            # to open tickets at the end of every certification run, and by
            # SchemaWatchAgent to bundle schema-drift remediations under an epic.
            "jira_create_ticket",
            "jira_create_epic",
        ],
        "integrations": [
            "slack_notify",
            "teams_bot",
            "email_intake",
            "servicenow",
        ],
        "aerospace_defense": [
            "contract_lookup",
            "cnc_code_review",
            "erp_write",
            "design_assistant",
        ],
        # Nuclear Operations & Reliability — STP demo (Phase 2).
        # 12 specialist actions across 4 use cases (policy lookup, PM
        # history, issue analysis, predictive maintenance) plus the
        # router glue. See docs/stp-demo-script.md for the full plan.
        "nuclear_operations": [
            # UC-1: Policy & Procedure Lookup
            "policy_search",
            "policy_cite_extract",
            # UC-2: Equipment Maintenance History
            "oracle_pm_lookup",
            "engineer_attribution",
            "wp_attachment_fetch",
            # UC-3: Equipment Issue Analysis
            "wp_corpus_search",
            "failure_mode_aggregate",
            # UC-4: Predictive Maintenance
            "rul_predict",
            "anomaly_detect",
            "pm_recommend",
            "risk_score_compute",
            # Cross-cutting: ChatSTP router classifier
            "intent_classify",
        ],
        # Agentic Enterprise (66 Degrees vendor-neutral) — split across
        # three specific industries so the Actions page collapses to just
        # the relevant actions when a single use case is selected in the
        # demoMode dropdown.
        "supply_chain_orchestrator": [
            "check_inventory",
            "find_alternative_supplier",
            "draft_purchase_order",
            "submit_for_approval",
        ],
        "hospitality": [
            "rag_faq_lookup",
            "booking_modify",
            "sentiment_score",
            "agent_assist_handoff",
        ],
        "commercial_real_estate": [
            "lease_extract",
            "lease_index",
            "duckdb_query",
        ],
        # Telecommunications — first-class industry for carrier far-edge ops.
        # 4 agents: CertificationAgent (parse + classify), SchemaWatchAgent
        # (detect_schema_drift), UpgradeAdvisorAgent (validate_upgrade_path),
        # MentorAgent (mentor_query). ApexSignal risk scoring is shared via
        # compute_risk_scores. Launch customer demo: Verizon Far Edge Operations
        # (demoMode='verizon_far_edge' rolls up to this industry).
        "telecommunications": [
            "parse_robot_output",      # CertificationAgent
            "classify_failures",       # CertificationAgent
            "detect_schema_drift",     # SchemaWatchAgent
            "validate_upgrade_path",   # UpgradeAdvisorAgent
            "compute_risk_scores",     # ApexSignal (wave-risk model)
            "mentor_query",            # MentorAgent
            # New-platform onboarding orchestration (OrchestratorAgent + PlaybookAgent)
            "design_test_coverage",    # OrchestratorAgent — propose PROPOSED-* tests
            "run_test_iterations",     # OrchestratorAgent — multi-iteration execution
            "analyze_playbook_gaps",   # PlaybookAgent — gap analysis
            "draft_playbook_change",   # PlaybookAgent — change-spec draft
            "apply_playbook_change",   # PlaybookAgent — commit/PR (direct action)
        ],
        # Oil & Gas Midstream — first-class industry for pipeline/NGL/crude
        # operators. 6 use cases for the EPROD demo:
        #   • InvoiceAgent     — invoice extraction + line-item validation
        #   • POAgent          — PO ↔ contract / MSA validation
        #   • VendorAgent      — Non-PO MSA validation at intake
        #   • QuoteAgent       — engineering quote reconciliation
        #   • TariffAgent      — FERC tariff sheet validation (wow use case)
        #   • JIBAgent         — JIB statement reconciliation vs AFE (wow use case)
        # Launch customer demo: Enterprise Products Partners (demoMode='eprod').
        "oil_gas_midstream": [
            "invoice_extract",         # InvoiceAgent
            "invoice_validate",        # InvoiceAgent
            "po_extract",              # POAgent
            "po_contract_validate",    # POAgent
            "msa_lookup",              # VendorAgent
            "non_po_msa_validate",     # VendorAgent
            "quote_extract",           # QuoteAgent
            "quote_reconcile",         # QuoteAgent
            "tariff_extract",          # TariffAgent (wow)
            "tariff_invoice_validate", # TariffAgent (wow)
            "jib_extract",             # JIBAgent (wow)
            "jib_afe_reconcile",       # JIBAgent (wow)
        ],
        # ─── Credit Union (CommunityWide FCU demo) ───
        # 5 agents covering NCUA-chartered credit union back-office:
        #   • MemberOnboardingAgent — CIP, OFAC, PEP, account opening
        #   • ComplianceAgent       — BSA/AML, SAR, CTR, CDD, NCUA exam prep
        #   • LoanDocumentAgent     — auto / HELOC / mortgage / personal packets
        #   • VendorContractAgent   — 47 contracts, SLA, rate drift, renewals
        #   • PolicyHRAgent         — policy acks, BSA training, board resolutions
        # Launch customer demo: CommunityWide FCU (demoMode='cwfcu').
        "credit_union": [
            "cip_ingest",                  # Onboarding
            "verify_government_id",        # Onboarding
            "ofac_screen",                 # Onboarding + Compliance
            "pep_screen",                  # Onboarding + Compliance
            "cip_calculate_risk_tier",     # Onboarding
            "detect_pattern",              # Compliance
            "draft_sar_narrative",         # Compliance
            "draft_ctr",                   # Compliance
            "cdd_assemble_packet",         # Compliance
            "loan_extract",                # Loan Document
            "loan_cross_validate_income",  # Loan Document
            "calculate_dti_ltv",           # Loan Document
            "vendor_monitor",              # Vendor & Contract
            "policy_ack_track",            # Policy & HR
            "ncua_aggregate_scores",       # Cross-agent · NCUA exam playbook
        ],
        # ─── Manufacturing · Multi-Division (The Boler Company demo) ───
        # 5 agents covering 5-division benefits allocation:
        #   • BEN — Benefits Operations Agent
        #   • EXC — Exceptions & Reconciliation Agent
        #   • JE  — Journal Entry Agent
        #   • SIG — Apex Signal Agent
        #   • AUD — Audit & Compliance Agent
        # Launch customer demo: The Boler Company (demoMode='boler').
        "manufacturing_multi_division": [
            "carrier_file_extract",         # Ingest
            "match_employee_roster",        # Ingest
            "lookup_division",              # Ingest
            "detect_exception",             # Exception detection
            "detect_carrier_drift",         # Exception detection
            "draft_reclassification",       # Exception detection
            "benefits_manager_review",      # Two-stage approval
            "cfo_signoff",                  # Two-stage approval
            "draft_journal_entry",          # JE + distribution
            "distribute_to_division_s3",    # JE + distribution
        ],
    }

    def __init__(self, actions_base_path: Optional[str] = None):
        """Initialize the registry with the base path to actions"""
        if actions_base_path:
            self.actions_path = Path(actions_base_path)
        else:
            # Default to actions directory relative to this file
            self.actions_path = Path(__file__).parent.parent.parent / "actions"

        self._registry: Dict[str, RegisteredAction] = {}
        self._loaded = False

    def discover_actions(self) -> List[RegisteredAction]:
        """
        Discover all actions in the actions directory structure.
        Returns list of discovered actions.
        """
        discovered = []

        for industry, actions in self.INDUSTRY_ACTIONS.items():
            industry_path = self.actions_path / industry

            if not industry_path.exists():
                continue

            for action_name in actions:
                action_path = industry_path / action_name
                handler_file = action_path / "handler.py"

                if handler_file.exists():
                    action_id = f"{industry}.{action_name}"

                    # Extract real schemas from the handler file:
                    # 1) @apex_action(ApexActionSchema(...)) decorator (best)
                    # 2) Google/Apex-style docstring
                    # 3) `return {...}` dict literals (output-only fallback)
                    try:
                        input_schema, output_schema = extract_schemas(
                            str(handler_file), action_name
                        )
                    except Exception:
                        # Never let schema extraction break discovery — fall
                        # back to empty schemas; the UI has empty-state copy
                        # for this case.
                        input_schema, output_schema = {}, {}

                    action = RegisteredAction(
                        action_id=action_id,
                        name=action_name,
                        description=f"{action_name.replace('_', ' ').title()} for {industry}",
                        category=self._get_category_for_industry(industry),
                        industry=industry,
                        handler_path=str(handler_file),
                        input_schema=input_schema,
                        output_schema=output_schema,
                    )
                    discovered.append(action)
                    self._registry[action_id] = action

        self._loaded = True
        return discovered

    def _get_category_for_industry(self, industry: str) -> str:
        """Map industry to category"""
        category_map = {
            "healthcare_payers": "claims",
            "healthcare_providers": "patient_management",
            "healthcare_clinical": "clinical_support",
            "retail": "commerce",
            "cpg": "compliance",
            "insurance_underwriting": "underwriting",
            "contact_center": "analytics",
            "airlines": "operations",
            "supply_chain": "logistics",
            "manufacturing": "operations",
            "hr": "human_resources",
            "financial_services": "finance",
            "core": "general",
            "integrations": "integrations",
            "aerospace_defense": "aerospace_defense",
            "nuclear_operations": "nuclear_operations",
            "supply_chain_orchestrator": "agentic_orchestration",
            "hospitality":              "customer_engagement",
            "commercial_real_estate":   "document_ai",
            "telecommunications":       "telco_far_edge",
            "oil_gas_midstream":        "midstream_document_intelligence",
            "credit_union":             "credit_union_intelligence",
            "manufacturing_multi_division": "manufacturing_multi_division_intelligence",
        }
        return category_map.get(industry, "other")

    def load_handler(self, action_id: str) -> Optional[callable]:
        """
        Dynamically load and return the handler function for an action.
        """
        if action_id not in self._registry:
            return None

        action = self._registry[action_id]

        if action.handler_function:
            return action.handler_function

        try:
            spec = importlib.util.spec_from_file_location(
                f"action_{action_id}",
                action.handler_path
            )
            module = importlib.util.module_from_spec(spec)

            # Add necessary paths for imports
            parent_path = str(Path(action.handler_path).parent.parent.parent)
            if parent_path not in sys.path:
                sys.path.insert(0, parent_path)

            spec.loader.exec_module(module)

            # Get the handler function (usually named after the action)
            handler_func = getattr(module, action.name, None)
            if handler_func is None:
                # Try getting the Lambda handler
                handler_func = getattr(module, 'handler', None)

            action.handler_function = handler_func
            return handler_func

        except Exception as e:
            print(f"Error loading handler for {action_id}: {e}")
            return None

    def get_action(self, action_id: str) -> Optional[RegisteredAction]:
        """Get a registered action by ID"""
        if not self._loaded:
            self.discover_actions()
        return self._registry.get(action_id)

    def get_actions_by_industry(self, industry: str) -> List[RegisteredAction]:
        """Get all actions for a specific industry"""
        if not self._loaded:
            self.discover_actions()
        return [a for a in self._registry.values() if a.industry == industry]

    def get_all_actions(self) -> List[RegisteredAction]:
        """Get all registered actions"""
        if not self._loaded:
            self.discover_actions()
        return list(self._registry.values())

    def invoke_action(self, action_id: str, **kwargs) -> Dict[str, Any]:
        """
        Invoke an action with the given parameters.

        Synchronous convenience wrapper. If the handler is async, this will
        run it in a fresh event loop. Prefer `invoke_action_async` from
        async contexts (FastAPI routes).
        """
        handler = self.load_handler(action_id)

        if not handler:
            return {
                "error": f"Handler not found for action {action_id}",
                "status": "failed",
            }

        try:
            result = handler(**kwargs)
            if inspect.iscoroutine(result):
                result = asyncio.run(result)
            return result
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "action_id": action_id,
            }

    async def invoke_action_async(self, action_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke an action from an async context.

        Returns a structured envelope so the caller can always render a
        predictable UI, even when the handler itself fails to load or raises:

          {
            "ok":         bool,
            "result":     dict | None,    # handler return value on success
            "error":      str  | None,    # single-line error message
            "error_type": str  | None,    # "not_found" | "load_failed" |
                                          # "bad_arguments" | "runtime"
            "traceback":  str  | None,    # multi-line Python traceback (runtime only)
            "duration_ms": int,           # measured wall-clock from load→return
          }
        """
        started = time.perf_counter()

        def elapsed_ms() -> int:
            return int((time.perf_counter() - started) * 1000)

        if action_id not in self._registry:
            return {
                "ok": False,
                "result": None,
                "error": f"Action {action_id} is not registered",
                "error_type": "not_found",
                "traceback": None,
                "duration_ms": elapsed_ms(),
            }

        try:
            handler = self.load_handler(action_id)
        except Exception as e:
            return {
                "ok": False,
                "result": None,
                "error": f"Handler failed to load: {e}",
                "error_type": "load_failed",
                "traceback": traceback.format_exc(),
                "duration_ms": elapsed_ms(),
            }

        if handler is None:
            return {
                "ok": False,
                "result": None,
                "error": "Handler could not be loaded (missing dependencies?)",
                "error_type": "load_failed",
                "traceback": None,
                "duration_ms": elapsed_ms(),
            }

        # Call the handler. Support both `handler(**kwargs)` convention AND
        # Lambda-style `handler(event, context)` convention. We try kwargs
        # first; on TypeError, retry with a single positional event dict.
        try:
            try:
                raw = handler(**payload)
            except TypeError:
                raw = handler(payload, None)

            if inspect.iscoroutine(raw):
                raw = await raw

            # Handler contract: return dict-like. Wrap primitives so the UI can render.
            if not isinstance(raw, dict):
                raw = {"result": raw}

            # Some handlers include their own `error` field on failure.
            if raw.get("status") == "failed" or "error" in raw:
                return {
                    "ok": False,
                    "result": raw,
                    "error": str(raw.get("error") or "Handler reported failure"),
                    "error_type": "runtime",
                    "traceback": None,
                    "duration_ms": elapsed_ms(),
                }

            return {
                "ok": True,
                "result": raw,
                "error": None,
                "error_type": None,
                "traceback": None,
                "duration_ms": elapsed_ms(),
            }
        except TypeError as e:
            return {
                "ok": False,
                "result": None,
                "error": f"Bad arguments: {e}",
                "error_type": "bad_arguments",
                "traceback": traceback.format_exc(),
                "duration_ms": elapsed_ms(),
            }
        except Exception as e:
            return {
                "ok": False,
                "result": None,
                "error": str(e),
                "error_type": "runtime",
                "traceback": traceback.format_exc(),
                "duration_ms": elapsed_ms(),
            }

    def get_action_metadata(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all actions suitable for API response.
        """
        if not self._loaded:
            self.discover_actions()

        return [
            {
                "action_id": action.action_id,
                "name": action.name,
                "description": action.description,
                "category": action.category,
                "industry": action.industry,
                "handler_path": action.handler_path,
                "status": "available",
            }
            for action in self._registry.values()
        ]


# Global registry instance
_registry: Optional[ActionRegistry] = None


def get_registry() -> ActionRegistry:
    """Get or create the global action registry"""
    global _registry
    if _registry is None:
        _registry = ActionRegistry()
        _registry.discover_actions()
    return _registry


def reload_registry() -> ActionRegistry:
    """
    Force a fresh discovery, discarding the cached singleton.
    Call this when handler files change on disk, the schema extractor
    has been updated, or you need to pick up new schemas without a
    backend restart.
    """
    global _registry
    _registry = ActionRegistry()
    _registry.discover_actions()
    return _registry


def register_actions_to_db(db_service, table_name: str = "apex-actions"):
    """
    Register all discovered actions to Cosmos DB.
    Called during system initialization.
    """
    registry = get_registry()
    registered = []

    for action in registry.get_all_actions():
        item = {
            "action_id": action.action_id,
            "name": action.name,
            "description": action.description,
            "category": action.category,
            "industry": action.industry,
            "type": "lambda",
            "status": "active",
            "input_schema": action.input_schema,
            "output_schema": action.output_schema,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        try:
            db_service.put_item(item)
            registered.append(action.action_id)
        except Exception as e:
            print(f"Error registering {action.action_id}: {e}")

    return registered
