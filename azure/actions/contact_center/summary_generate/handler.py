"""
Summary Generate - Small Factory
Generates a structured summary of the conversation.

Supports AI-enhanced summarization via Claude when available,
with fallback to rule-based extraction.
"""

from typing import Dict, Any, List
import structlog
from services.small_factory import register_factory

# Claude integration (optional - graceful fallback)
try:
    from services.azure_openai import get_model_router
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False

logger = structlog.get_logger()


def truncate_text(text: str, max_words: int) -> str:
    """Truncate text to max words."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + '...'


@register_factory("summary_generate")
async def summary_generate(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a structured summary of the conversation.

    Input:
        claim: Extracted claim details
        sentiment: Sentiment analysis
        compliance: Compliance audit
        config.max_length: Maximum summary length (words)
        config.include_sections: Sections to include

    Output:
        summary: Full summary text
        sections: Individual section summaries
        key_facts: Bullet points of key facts
        action_items: Required follow-up actions
    """
    config = input_data.get('config', {})
    claim_output = input_data.get('claim', {})
    sentiment_output = input_data.get('sentiment', {})
    compliance_output = input_data.get('compliance', {})
    transcribe_output = input_data.get('transcribe', {})
    diarize_output = input_data.get('diarize', {})
    state = input_data.get('state', {})

    max_length = config.get('max_length', 250)
    include_sections = config.get('include_sections', ['key_facts', 'sentiment_summary', 'compliance_notes', 'recommended_actions'])

    # Get basic info
    full_text = transcribe_output.get('full_text', '')
    if not full_text:
        full_text = state.get('input', {}).get('transcript', {}).get('full_text', '')

    word_count = len(full_text.split())
    duration = transcribe_output.get('duration_seconds', 0)

    # Build sections
    sections = {}

    # Key Facts Section
    if 'key_facts' in include_sections:
        claim_type = claim_output.get('claim_type', 'unknown')
        claim_details = claim_output.get('claim_details', {})
        entities = claim_output.get('extracted_entities', {})

        key_facts = []

        # Claim type
        if claim_type != 'unknown':
            key_facts.append(f"Claim type: {claim_type.replace('_', ' ').title()}")

        # Claimant
        if entities.get('claimant_name'):
            key_facts.append(f"Claimant: {entities['claimant_name']}")

        # Policy number
        if entities.get('policy_number'):
            key_facts.append(f"Policy: {entities['policy_number']}")

        # Incident date
        if entities.get('incident_date'):
            key_facts.append(f"Incident date: {entities['incident_date']}")

        # Damage amount
        if entities.get('damage_amount'):
            key_facts.append(f"Estimated damage: {entities['damage_amount']}")

        # Vehicle info
        if entities.get('vehicle'):
            key_facts.append(f"Vehicle: {entities['vehicle']}")

        sections['key_facts'] = key_facts

    # Sentiment Summary Section
    if 'sentiment_summary' in include_sections:
        overall_sentiment = sentiment_output.get('overall_sentiment', 'neutral')
        sentiment_arc = sentiment_output.get('sentiment_arc', 'stable')
        avg_score = sentiment_output.get('average_score', 0)

        sentiment_text = f"Customer sentiment was {overall_sentiment}"
        if sentiment_arc == 'improving':
            sentiment_text += ", improving throughout the call"
        elif sentiment_arc == 'declining':
            sentiment_text += ", declining as the call progressed"
        else:
            sentiment_text += " throughout the call"

        # Speaker-specific sentiment
        by_speaker = sentiment_output.get('by_speaker', {})
        customer_sentiment = None
        for speaker, data in by_speaker.items():
            if 'customer' in speaker.lower():
                customer_sentiment = data

        if customer_sentiment:
            sentiment_text += f". Customer expressed {customer_sentiment.get('sentiment', 'neutral')} sentiment overall."

        sections['sentiment_summary'] = sentiment_text

    # Compliance Notes Section
    if 'compliance_notes' in include_sections:
        compliance_score = compliance_output.get('overall_score', 0)
        violations = compliance_output.get('violations', [])
        passed = compliance_output.get('passed', True)

        if passed:
            compliance_text = f"Call met compliance standards (score: {compliance_score}/100)."
        else:
            violation_summary = ", ".join([v['rule'].replace('_', ' ') for v in violations[:3]])
            compliance_text = f"Compliance issues detected (score: {compliance_score}/100). Issues: {violation_summary}."

        sections['compliance_notes'] = compliance_text

    # Recommended Actions Section
    if 'recommended_actions' in include_sections:
        actions = []

        # Based on claim completeness
        missing_fields = claim_output.get('missing_fields', [])
        if missing_fields:
            actions.append(f"Collect missing information: {', '.join(missing_fields[:3])}")

        # Based on sentiment
        if sentiment_output.get('overall_sentiment') == 'negative':
            actions.append("Follow up to address customer concerns")

        # Based on compliance
        if not compliance_output.get('passed', True):
            actions.append("Review compliance violations with supervisor")

        # Based on claim actionability
        if claim_output.get('is_actionable'):
            actions.append("Process claim according to standard procedure")
        elif claim_output.get('requires_callback'):
            actions.append("Schedule callback to gather additional details")

        if not actions:
            actions.append("No immediate follow-up required")

        sections['recommended_actions'] = actions

    # Build full summary
    summary_parts = []

    # Opening
    claim_type = claim_output.get('claim_type', 'unknown')
    summary_parts.append(f"This call was regarding a {claim_type.replace('_', ' ')} claim.")

    # Key facts
    if sections.get('key_facts'):
        summary_parts.append("Key information captured includes: " + "; ".join(sections['key_facts'][:4]) + ".")

    # Sentiment
    if sections.get('sentiment_summary'):
        summary_parts.append(sections['sentiment_summary'])

    # Compliance
    if sections.get('compliance_notes'):
        summary_parts.append(sections['compliance_notes'])

    full_summary = " ".join(summary_parts)
    full_summary = truncate_text(full_summary, max_length)

    # Action items
    action_items = sections.get('recommended_actions', [])

    # Build rule-based result
    rule_based_result = {
        "summary": full_summary,
        "sections": sections,
        "key_facts": sections.get('key_facts', []),
        "action_items": action_items,
        "call_duration_seconds": duration,
        "word_count": word_count,
        "claim_type": claim_output.get('claim_type', 'unknown'),
        "requires_followup": len(action_items) > 1 or claim_output.get('requires_callback', False),
        "ai_enhanced": False
    }

    # Try AI-enhanced summarization if enabled
    use_ai = config.get('use_ai', True) and CLAUDE_ENABLED
    if use_ai and full_text:
        try:
            ai_result = await _generate_ai_summary(
                full_text,
                claim_output,
                sentiment_output,
                compliance_output
            )
            if ai_result:
                # Merge AI insights with rule-based data
                rule_based_result["summary"] = ai_result.get("summary", full_summary)
                rule_based_result["key_facts"] = ai_result.get("key_facts", sections.get('key_facts', []))
                rule_based_result["action_items"] = ai_result.get("action_items", action_items)
                rule_based_result["requires_followup"] = ai_result.get("requires_followup", rule_based_result["requires_followup"])
                rule_based_result["ai_enhanced"] = True
                rule_based_result["ai_insights"] = {
                    "next_steps": ai_result.get("next_steps"),
                    "customer_concern_resolved": ai_result.get("customer_concern_resolved"),
                }
                logger.info("AI-enhanced summary generated successfully")
        except Exception as e:
            logger.warning("AI summary failed, using rule-based", error=str(e))

    return rule_based_result


async def _generate_ai_summary(
    transcript: str,
    claim_data: Dict[str, Any],
    sentiment_data: Dict[str, Any],
    compliance_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate AI-enhanced summary using Claude."""
    if not CLAUDE_ENABLED:
        return None

    claude = get_model_router()
    context = {
        "claim_data": claim_data,
        "sentiment_data": {
            "overall": sentiment_data.get("overall_sentiment"),
            "arc": sentiment_data.get("sentiment_arc"),
            "score": sentiment_data.get("average_score")
        },
        "compliance_data": {
            "passed": compliance_data.get("passed"),
            "score": compliance_data.get("overall_score"),
            "violations": [v.get("rule") for v in compliance_data.get("violations", [])]
        }
    }

    result = await claude.analyze_conversation(
        transcript=transcript,
        analysis_type="summary",
        context=context
    )

    if result.get("success") and result.get("parsed"):
        return result["parsed"]

    return None
