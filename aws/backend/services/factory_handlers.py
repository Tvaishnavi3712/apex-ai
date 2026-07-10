"""
Factory Handlers Registration
Auto-imports all Small Factory handlers to register them with the engine.
"""

import structlog
import sys
from pathlib import Path

logger = structlog.get_logger()

# Add actions directory to path
ACTIONS_DIR = Path(__file__).parent.parent.parent / "actions"
if str(ACTIONS_DIR) not in sys.path:
    sys.path.insert(0, str(ACTIONS_DIR))


def register_all_handlers():
    """
    Import all Small Factory handlers to register them with the engine.

    This function imports the handler modules which triggers the @register_factory
    decorator, automatically registering each handler with the SmallFactoryEngine.
    """
    handlers_registered = []
    errors = []

    # Core handlers
    core_handlers = [
        ("actions.core.transcribe_audio.handler", "transcribe_audio"),
        ("actions.core.diarize_speakers.handler", "diarize_speakers"),
    ]

    # Contact center handlers
    contact_center_handlers = [
        ("actions.contact_center.intent_classify.handler", "intent_classify"),
        ("actions.contact_center.sentiment_timeline.handler", "sentiment_timeline"),
        ("actions.contact_center.entity_extract.handler", "entity_extract"),
        ("actions.contact_center.compliance_audit.handler", "compliance_audit"),
        ("actions.contact_center.summary_generate.handler", "summary_generate"),
        ("actions.contact_center.escalation_detect.handler", "escalation_detect_factory"),
        ("actions.contact_center.quality_score.handler", "quality_score_factory"),
        ("actions.contact_center.coaching_recommend.handler", "coaching_tips_factory"),
    ]

    # Insurance underwriting handlers
    insurance_handlers = [
        ("actions.insurance_underwriting.claim_extract.handler", "claim_extract"),
        ("actions.insurance_underwriting.fraud_indicators.handler", "fraud_indicators"),
        ("actions.insurance_underwriting.priority_calculate.handler", "priority_calculate"),
        ("actions.insurance_underwriting.auto_decision.handler", "auto_decision_factory"),
    ]

    # Financial services handlers (Invoice Processing Chain)
    financial_handlers = [
        ("actions.financial_services.email_parse.handler", "email_parse"),
        ("actions.financial_services.vendor_match.handler", "vendor_match"),
        ("actions.financial_services.po_reconcile.handler", "po_reconcile"),
        ("actions.financial_services.approval_route.handler", "approval_route"),
        ("actions.financial_services.erp_post.handler", "erp_post"),
    ]

    # Healthcare provider handlers (Patient Record Chain)
    healthcare_handlers = [
        ("actions.healthcare_providers.patient_identify.handler", "patient_identify"),
        ("actions.healthcare_providers.clinical_extract.handler", "clinical_extract"),
        ("actions.healthcare_providers.code_suggest.handler", "code_suggest"),
        ("actions.healthcare_providers.quality_audit.handler", "quality_audit"),
        ("actions.healthcare_providers.ehr_format.handler", "ehr_format"),
    ]

    # HR handlers (Onboarding Chain)
    hr_handlers = [
        ("actions.hr.identity_verify.handler", "identity_verify"),
        ("actions.hr.i9_validate.handler", "i9_validate"),
        ("actions.hr.background_check.handler", "background_check"),
        ("actions.hr.benefits_enroll.handler", "benefits_enroll"),
        ("actions.hr.provisioning_trigger.handler", "provisioning_trigger"),
    ]

    # Healthcare Payers handlers (Claims Processing Chain)
    healthcare_payers_handlers = [
        ("actions.healthcare_payers.claims_adjudication.handler", "claims_adjudication"),
        ("actions.healthcare_payers.eligibility_verify.handler", "eligibility_verify"),
        ("actions.healthcare_payers.fraud_detection.handler", "fraud_detection"),
        ("actions.healthcare_payers.payment_calculate.handler", "payment_calculate"),
        ("actions.healthcare_payers.medical_necessity.handler", "medical_necessity_check"),
    ]

    # Sales AI handlers (Sales Interaction Agent Chain)
    sales_ai_handlers = [
        ("actions.sales_ai.emotion_analyze.handler", "emotion_analyze"),
        ("actions.sales_ai.buying_signals.handler", "buying_signals"),
        ("actions.sales_ai.objection_detect.handler", "objection_detect"),
        ("actions.sales_ai.competitor_mentions.handler", "competitor_mentions"),
        ("actions.sales_ai.deal_intelligence.handler", "deal_intelligence"),
        ("actions.sales_ai.sales_coaching.handler", "sales_coaching"),
        ("actions.sales_ai.sales_summary.handler", "sales_summary"),
    ]

    all_handlers = (
        core_handlers +
        contact_center_handlers +
        insurance_handlers +
        financial_handlers +
        healthcare_handlers +
        hr_handlers +
        healthcare_payers_handlers +
        sales_ai_handlers
    )

    for module_path, handler_name in all_handlers:
        try:
            # Import the module (triggers @register_factory decorator)
            __import__(module_path)
            handlers_registered.append(handler_name)
            logger.debug("Registered handler", handler=handler_name)
        except ImportError as e:
            errors.append({"handler": handler_name, "error": str(e)})
            logger.warning("Failed to register handler", handler=handler_name, error=str(e))
        except Exception as e:
            errors.append({"handler": handler_name, "error": str(e)})
            logger.error("Error registering handler", handler=handler_name, error=str(e))

    logger.info(
        "Factory handlers registration complete",
        registered=len(handlers_registered),
        failed=len(errors)
    )

    return {
        "registered": handlers_registered,
        "errors": errors
    }


# Auto-register on import
_registration_result = None

def get_registration_status():
    """Get the registration status."""
    global _registration_result
    if _registration_result is None:
        _registration_result = register_all_handlers()
    return _registration_result
