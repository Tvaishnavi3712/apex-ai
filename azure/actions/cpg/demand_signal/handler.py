"""
Demand Signal - CPG Action (Context-Driven)
Process and analyze demand signals from retailers

Context-Driven Architecture:
- Signal processing from playbook context.signal_config
- Alert thresholds from context.alert_config
- Response rules from context.response_config
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import structlog

try:
    from services.small_factory import register_factory
    SMALL_FACTORY_ENABLED = True
except ImportError:
    SMALL_FACTORY_ENABLED = False
    def register_factory(name):
        def decorator(func):
            return func
        return decorator

logger = structlog.get_logger()


DEFAULT_SIGNAL_CONFIG = {
    "signal_types": ["pos", "inventory", "forecast", "order"],
    "aggregation_period": "daily",
    "variance_threshold_pct": 20
}


@register_factory("demand_signal")
async def demand_signal(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process demand signals (context-driven).

    Context keys used:
        - signal_config: Signal processing settings
        - alert_config: Alert thresholds
        - response_config: Auto-response rules

    Input:
        signals: Raw demand signal data
        product_info: Product information
        retailer: Retailer source

    Output:
        processed_signals: Processed signal data
        insights: Demand insights
        alerts: Triggered alerts
    """
    context = context or input_data.get('context', {})
    signal_config = context.get('signal_config', DEFAULT_SIGNAL_CONFIG)
    alert_config = context.get('alert_config', {})
    response_config = context.get('response_config', {})

    logger.info(
        "Demand signal invoked",
        context_driven=bool(context)
    )

    signals = input_data.get('signals', [])
    product_info = input_data.get('product_info', {})
    retailer = input_data.get('retailer', {})

    variance_threshold = signal_config.get('variance_threshold_pct', 20)
    aggregation = signal_config.get('aggregation_period', 'daily')

    # Process signals
    processed = []
    alerts = []

    for signal in signals:
        signal_type = signal.get('type', 'pos')
        value = signal.get('value', 0)
        baseline = signal.get('baseline', value)

        # Calculate variance
        variance_pct = ((value - baseline) / baseline * 100) if baseline > 0 else 0

        processed_signal = {
            'signal_id': signal.get('id'),
            'type': signal_type,
            'product_sku': signal.get('sku'),
            'value': value,
            'baseline': baseline,
            'variance_pct': round(variance_pct, 1),
            'period': signal.get('period'),
            'retailer': retailer.get('name')
        }
        processed.append(processed_signal)

        # Check for alerts
        if abs(variance_pct) >= variance_threshold:
            alert_type = 'surge' if variance_pct > 0 else 'decline'
            alerts.append({
                'type': f'demand_{alert_type}',
                'severity': 'high' if abs(variance_pct) >= variance_threshold * 2 else 'medium',
                'product_sku': signal.get('sku'),
                'variance_pct': round(variance_pct, 1),
                'message': f"Demand {alert_type}: {abs(round(variance_pct, 1))}% vs baseline"
            })

    # Generate insights
    insights = _generate_insights(processed, variance_threshold)

    # Determine recommended actions
    actions = _recommend_actions(alerts, response_config)

    return {
        "retailer": retailer.get('name'),
        "signals_processed": len(processed),
        "processed_signals": processed,
        "aggregation_period": aggregation,
        "variance_threshold": variance_threshold,
        "insights": insights,
        "alerts": alerts,
        "alert_count": len(alerts),
        "recommended_actions": actions,
        "processed_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "demand_signal",
        "factory_version": "2.0.0",
        "context_keys_used": ["signal_config", "alert_config", "response_config"]
    }


def _generate_insights(signals: List[Dict], threshold: float) -> List[Dict]:
    """Generate demand insights."""
    insights = []

    surges = [s for s in signals if s['variance_pct'] >= threshold]
    declines = [s for s in signals if s['variance_pct'] <= -threshold]

    if surges:
        insights.append({
            'type': 'demand_surge',
            'count': len(surges),
            'avg_variance': round(sum(s['variance_pct'] for s in surges) / len(surges), 1),
            'insight': f'{len(surges)} products showing demand surge'
        })

    if declines:
        insights.append({
            'type': 'demand_decline',
            'count': len(declines),
            'avg_variance': round(sum(s['variance_pct'] for s in declines) / len(declines), 1),
            'insight': f'{len(declines)} products showing demand decline'
        })

    return insights


def _recommend_actions(alerts: List[Dict], config: Dict) -> List[str]:
    """Recommend actions based on alerts."""
    actions = []

    high_alerts = [a for a in alerts if a.get('severity') == 'high']

    if any(a['type'] == 'demand_surge' for a in high_alerts):
        actions.append('Increase production/inventory for high-demand products')
        actions.append('Review supply chain capacity')

    if any(a['type'] == 'demand_decline' for a in high_alerts):
        actions.append('Investigate root cause of demand decline')
        actions.append('Consider promotional activity')

    return actions


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(demand_signal(event))
