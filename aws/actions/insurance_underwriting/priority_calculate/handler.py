"""
Priority Calculate - Small Factory
Calculates claim priority based on multiple factors.
"""

from typing import Dict, Any, List
from services.small_factory import register_factory


@register_factory("priority_calculate")
async def priority_calculate(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate claim priority score.

    Input:
        sentiment: Sentiment analysis results
        fraud: Fraud detection results
        compliance: Compliance audit results
        config.weights: Weight configuration

    Output:
        priority_score: Overall priority (0-100)
        priority_level: critical/high/medium/low
        factors: Individual factor scores
        recommended_sla: Suggested SLA in hours
    """
    config = input_data.get('config', {})
    sentiment_output = input_data.get('sentiment', {})
    fraud_output = input_data.get('fraud', {})
    compliance_output = input_data.get('compliance', {})

    weights = config.get('weights', {
        'sentiment': 0.3,
        'fraud_risk': 0.4,
        'compliance': 0.3
    })

    # Normalize weights
    total_weight = sum(weights.values())
    weights = {k: v / total_weight for k, v in weights.items()}

    # Calculate factor scores (all normalized to 0-100 where higher = higher priority)

    # Sentiment factor: negative sentiment = higher priority
    sentiment_score = sentiment_output.get('average_score', 0)  # -1 to 1
    sentiment_priority = int((1 - sentiment_score) * 50)  # 0 to 100, negative = high

    # Sentiment arc adjustment
    sentiment_arc = sentiment_output.get('sentiment_arc', 'stable')
    if sentiment_arc == 'declining':
        sentiment_priority = min(100, sentiment_priority + 15)
    elif sentiment_arc == 'improving':
        sentiment_priority = max(0, sentiment_priority - 10)

    # Fraud factor: high fraud risk = higher priority for investigation
    fraud_score = fraud_output.get('fraud_score', 0)  # 0 to 100
    fraud_priority = fraud_score  # Direct mapping

    # Compliance factor: violations = higher priority
    compliance_score = compliance_output.get('overall_score', 100)  # 0 to 100
    compliance_priority = 100 - compliance_score  # Invert: low compliance = high priority

    violation_count = compliance_output.get('violation_count', 0)
    if violation_count > 2:
        compliance_priority = min(100, compliance_priority + 20)

    # Calculate weighted priority
    factors = {
        'sentiment': {
            'score': sentiment_priority,
            'weight': weights.get('sentiment', 0.3),
            'weighted_score': sentiment_priority * weights.get('sentiment', 0.3)
        },
        'fraud_risk': {
            'score': fraud_priority,
            'weight': weights.get('fraud_risk', 0.4),
            'weighted_score': fraud_priority * weights.get('fraud_risk', 0.4)
        },
        'compliance': {
            'score': compliance_priority,
            'weight': weights.get('compliance', 0.3),
            'weighted_score': compliance_priority * weights.get('compliance', 0.3)
        }
    }

    priority_score = sum(f['weighted_score'] for f in factors.values())
    priority_score = round(min(100, max(0, priority_score)), 1)

    # Determine priority level
    if priority_score >= 80:
        priority_level = "critical"
        recommended_sla = 2  # hours
    elif priority_score >= 60:
        priority_level = "high"
        recommended_sla = 8  # hours
    elif priority_score >= 40:
        priority_level = "medium"
        recommended_sla = 24  # hours
    else:
        priority_level = "low"
        recommended_sla = 72  # hours

    # Build reasoning
    reasoning = []
    if sentiment_priority > 60:
        reasoning.append("Customer expressed significant negative sentiment")
    if fraud_priority > 50:
        reasoning.append("Elevated fraud risk indicators detected")
    if compliance_priority > 50:
        reasoning.append("Compliance violations require attention")

    if not reasoning:
        reasoning.append("Standard processing priority")

    return {
        "priority_score": priority_score,
        "priority_level": priority_level,
        "factors": factors,
        "recommended_sla_hours": recommended_sla,
        "reasoning": reasoning,
        "requires_immediate_attention": priority_level in ["critical", "high"],
        "escalate_to_supervisor": priority_level == "critical"
    }
