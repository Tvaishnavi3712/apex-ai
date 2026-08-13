"""
Shelf Analyze - CPG Action (Context-Driven)
Analyze shelf placement and planogram compliance

Context-Driven Architecture:
- Planogram rules from playbook context.planogram_config
- Compliance thresholds from context.compliance_config
- Category rules from context.category_config
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
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


DEFAULT_PLANOGRAM_CONFIG = {
    "compliance_threshold_pct": 85,
    "check_facing_count": True,
    "check_position": True,
    "check_price_tag": True
}


@register_factory("shelf_analyze")
async def shelf_analyze(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze shelf compliance (context-driven).

    Context keys used:
        - planogram_config: Planogram requirements
        - compliance_config: Compliance thresholds
        - category_config: Category-specific rules

    Input:
        shelf_image: Shelf image or data
        store_info: Store information
        expected_planogram: Expected planogram

    Output:
        compliance_score: Overall compliance score
        compliance_details: Per-product compliance
        issues: Identified issues
    """
    context = context or input_data.get('context', {})
    planogram_config = context.get('planogram_config', DEFAULT_PLANOGRAM_CONFIG)
    compliance_config = context.get('compliance_config', {})

    logger.info(
        "Shelf analyze invoked",
        context_driven=bool(context)
    )

    shelf_data = input_data.get('shelf_data', {})
    store = input_data.get('store_info', {})
    expected = input_data.get('expected_planogram', {})

    threshold = planogram_config.get('compliance_threshold_pct', 85)

    # Analyze products (simulated)
    products = shelf_data.get('detected_products', [])
    expected_products = expected.get('products', [])

    compliance_details = []
    issues = []
    total_score = 0

    for expected_prod in expected_products:
        sku = expected_prod.get('sku')
        detected = next((p for p in products if p.get('sku') == sku), None)

        prod_score = 0
        prod_issues = []

        if not detected:
            prod_issues.append('Product not detected on shelf')
        else:
            # Check facings
            if planogram_config.get('check_facing_count', True):
                expected_facings = expected_prod.get('facings', 1)
                actual_facings = detected.get('facings', 0)
                if actual_facings >= expected_facings:
                    prod_score += 40
                else:
                    prod_issues.append(f'Low facings: {actual_facings}/{expected_facings}')
                    prod_score += 20

            # Check position
            if planogram_config.get('check_position', True):
                expected_pos = expected_prod.get('position', {})
                actual_pos = detected.get('position', {})
                if expected_pos.get('shelf') == actual_pos.get('shelf'):
                    prod_score += 30
                else:
                    prod_issues.append('Incorrect shelf position')

            # Check price tag
            if planogram_config.get('check_price_tag', True):
                if detected.get('price_tag_visible', False):
                    prod_score += 30
                else:
                    prod_issues.append('Price tag not visible')
                    prod_score += 10

        compliance_details.append({
            'sku': sku,
            'product_name': expected_prod.get('name'),
            'detected': detected is not None,
            'compliance_score': prod_score,
            'issues': prod_issues
        })

        total_score += prod_score
        issues.extend([f"{sku}: {i}" for i in prod_issues])

    # Calculate overall compliance
    max_score = len(expected_products) * 100
    overall_score = (total_score / max_score * 100) if max_score > 0 else 0
    meets_threshold = overall_score >= threshold

    return {
        "store_id": store.get('store_id'),
        "store_name": store.get('name'),
        "compliance_score": round(overall_score, 1),
        "compliance_threshold": threshold,
        "meets_threshold": meets_threshold,
        "compliance_details": compliance_details,
        "products_expected": len(expected_products),
        "products_detected": len([d for d in compliance_details if d['detected']]),
        "issues": issues,
        "issue_count": len(issues),
        "recommendations": _get_recommendations(compliance_details),
        "analyzed_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "shelf_analyze",
        "factory_version": "2.0.0",
        "context_keys_used": ["planogram_config", "compliance_config", "category_config"]
    }


def _get_recommendations(details: List[Dict]) -> List[str]:
    """Generate recommendations based on compliance details."""
    recommendations = []

    missing = [d for d in details if not d['detected']]
    if missing:
        recommendations.append(f"Restock {len(missing)} missing products")

    low_score = [d for d in details if d['compliance_score'] < 50]
    if low_score:
        recommendations.append(f"Fix placement for {len(low_score)} products")

    return recommendations


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(shelf_analyze(event))
