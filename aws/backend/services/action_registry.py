"""
Action Registry Service
Discovers and manages all action handlers across industries
"""
import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


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
            "dynamodb_lookup",
            "s3_operations",
            "notification",
        ],
        "integrations": [
            "slack_notify",
            "teams_bot",
            "email_intake",
            "servicenow",
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
                    action = RegisteredAction(
                        action_id=action_id,
                        name=action_name,
                        description=f"{action_name.replace('_', ' ').title()} for {industry}",
                        category=self._get_category_for_industry(industry),
                        industry=industry,
                        handler_path=str(handler_file),
                        input_schema={},
                        output_schema={},
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
        Returns the action result.
        """
        handler = self.load_handler(action_id)

        if not handler:
            return {
                "error": f"Handler not found for action {action_id}",
                "status": "failed"
            }

        try:
            result = handler(**kwargs)
            return result
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "action_id": action_id
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


def register_actions_to_db(db_service, table_name: str = "apex-actions"):
    """
    Register all discovered actions to DynamoDB.
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
