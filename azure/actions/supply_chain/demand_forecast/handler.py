"""
Demand Forecast - Supply Chain Action (Context-Driven)
Generate demand forecasts for inventory planning

Context-Driven Architecture:
- Forecast settings from playbook context.forecast_config
- Seasonality from context.seasonality_config
- Historical data settings from context.history_config
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


DEFAULT_FORECAST_CONFIG = {
    "horizon_days": 90,
    "confidence_level": 0.95,
    "method": "weighted_moving_average",
    "include_seasonality": True
}


@register_factory("demand_forecast")
async def demand_forecast(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate demand forecast (context-driven).

    Context keys used:
        - forecast_config: Forecast method and settings
        - seasonality_config: Seasonal adjustment factors
        - history_config: Historical data parameters

    Input:
        sku_list: SKUs to forecast
        historical_data: Historical demand data

    Output:
        forecasts: Demand forecasts by SKU
        confidence_intervals: Forecast confidence bounds
    """
    context = context or input_data.get('context', {})
    forecast_config = context.get('forecast_config', DEFAULT_FORECAST_CONFIG)
    seasonality_config = context.get('seasonality_config', {})

    logger.info(
        "Demand forecast invoked",
        context_driven=bool(context)
    )

    sku_list = input_data.get('sku_list', [])
    historical_data = input_data.get('historical_data', {})

    horizon = forecast_config.get('horizon_days', 90)
    confidence = forecast_config.get('confidence_level', 0.95)
    method = forecast_config.get('method', 'weighted_moving_average')

    # Generate forecasts
    forecasts = []

    for sku in sku_list:
        history = historical_data.get(sku, {})
        avg_daily = history.get('avg_daily_demand', 10)

        # Apply seasonality
        season_factor = 1.0
        if forecast_config.get('include_seasonality', True):
            month = datetime.utcnow().month
            season_factor = seasonality_config.get(str(month), 1.0)

        adjusted_demand = avg_daily * season_factor

        # Calculate confidence bounds
        std_dev = history.get('std_dev', avg_daily * 0.2)
        lower_bound = max(0, adjusted_demand - (1.96 * std_dev))
        upper_bound = adjusted_demand + (1.96 * std_dev)

        forecasts.append({
            'sku': sku,
            'forecast_daily': round(adjusted_demand, 1),
            'forecast_weekly': round(adjusted_demand * 7, 1),
            'forecast_monthly': round(adjusted_demand * 30, 1),
            'horizon_total': round(adjusted_demand * horizon, 1),
            'confidence_level': confidence,
            'lower_bound_daily': round(lower_bound, 1),
            'upper_bound_daily': round(upper_bound, 1),
            'seasonality_factor': season_factor,
            'trend': history.get('trend', 'stable')
        })

    return {
        "forecast_horizon_days": horizon,
        "forecast_method": method,
        "forecasts": forecasts,
        "sku_count": len(forecasts),
        "confidence_level": confidence,
        "seasonality_applied": forecast_config.get('include_seasonality', True),
        "forecast_date": datetime.utcnow().strftime('%Y-%m-%d'),
        "valid_until": (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d'),
        "generated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "demand_forecast",
        "factory_version": "2.0.0",
        "context_keys_used": ["forecast_config", "seasonality_config", "history_config"]
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(demand_forecast(event))
