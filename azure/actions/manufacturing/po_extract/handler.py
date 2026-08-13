"""
PO Extract - Manufacturing Action (Context-Driven)
Extract purchase order data from documents

Context-Driven Architecture:
- Extraction fields from playbook context.extraction_config
- Validation rules from context.po_validation
- Supplier mappings from context.supplier_config
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


# Default extraction configuration
DEFAULT_EXTRACTION_CONFIG = {
    "extract_fields": [
        "po_number", "vendor_info", "ship_to", "bill_to",
        "line_items", "total_amount", "payment_terms", "delivery_date"
    ],
    "confidence_threshold": 0.85,
    "validate_totals": True
}

# Default PO validation rules
DEFAULT_PO_VALIDATION = {
    "require_po_number": True,
    "require_vendor": True,
    "max_line_items": 100,
    "validate_item_numbers": True
}


@register_factory("po_extract")
async def po_extract(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract purchase order data (context-driven).

    Context keys used:
        - extraction_config: Fields to extract and thresholds
        - po_validation: PO validation rules
        - supplier_config: Supplier mapping configurations

    Input:
        document_content: Raw PO document content
        document_type: Type of PO document

    Output:
        po_data: Extracted PO information
        line_items: Extracted line items
        validation_results: Validation results
    """
    context = context or input_data.get('context', {})
    extraction_config = context.get('extraction_config', DEFAULT_EXTRACTION_CONFIG)
    po_validation = context.get('po_validation', DEFAULT_PO_VALIDATION)
    supplier_config = context.get('supplier_config', {})

    logger.info(
        "PO extract invoked",
        context_driven=bool(context)
    )

    document_content = input_data.get('document_content', '')
    document_type = input_data.get('document_type', 'purchase_order')

    # Extract fields
    extract_fields = extraction_config.get('extract_fields', DEFAULT_EXTRACTION_CONFIG['extract_fields'])
    confidence_threshold = extraction_config.get('confidence_threshold', 0.85)

    # Simulated extraction
    extracted_data = {
        "po_number": f"PO{datetime.utcnow().strftime('%Y%m%d')}-001",
        "po_date": datetime.utcnow().strftime('%Y-%m-%d'),
        "vendor_info": {
            "vendor_id": "VND-001",
            "vendor_name": "ABC Supplies Inc.",
            "address": {
                "street": "123 Industrial Way",
                "city": "Manufacturing City",
                "state": "MC",
                "zip": "12345"
            },
            "contact": "John Vendor"
        },
        "ship_to": {
            "facility": "Main Plant",
            "address": "456 Production Blvd",
            "city": "Factory Town",
            "state": "FT",
            "zip": "67890"
        },
        "bill_to": {
            "company": "Manufacturing Corp",
            "address": "789 Corporate Drive",
            "city": "Business City",
            "state": "BC",
            "zip": "11223"
        },
        "line_items": [
            {
                "line_number": 1,
                "item_number": "PART-001",
                "description": "Steel Plate 4x8 ft",
                "quantity": 100,
                "unit": "EA",
                "unit_price": 45.00,
                "extended_price": 4500.00
            },
            {
                "line_number": 2,
                "item_number": "PART-002",
                "description": "Aluminum Sheet 3x6 ft",
                "quantity": 50,
                "unit": "EA",
                "unit_price": 32.00,
                "extended_price": 1600.00
            },
            {
                "line_number": 3,
                "item_number": "PART-003",
                "description": "Fastener Kit - Industrial",
                "quantity": 25,
                "unit": "KT",
                "unit_price": 85.00,
                "extended_price": 2125.00
            }
        ],
        "subtotal": 8225.00,
        "tax": 658.00,
        "shipping": 250.00,
        "total_amount": 9133.00,
        "payment_terms": "Net 30",
        "delivery_date": (datetime.utcnow().replace(day=1) + __import__('datetime').timedelta(days=45)).strftime('%Y-%m-%d'),
        "shipping_method": "Ground Freight",
        "special_instructions": "Deliver to receiving dock B"
    }

    # Calculate confidence scores
    confidence_scores = {}
    for field in extract_fields:
        if field in extracted_data:
            confidence_scores[field] = 0.94
        else:
            confidence_scores[field] = 0.0

    overall_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0

    # Validate PO data
    validation_results = _validate_po_data(extracted_data, po_validation)

    # Validate line item totals
    if extraction_config.get('validate_totals', True):
        totals_valid = _validate_totals(extracted_data)
        validation_results['totals'] = {
            'valid': totals_valid,
            'message': 'Line items sum to subtotal' if totals_valid else 'Total mismatch detected'
        }

    # Match vendor
    vendor_match = _match_vendor(extracted_data['vendor_info'], supplier_config)

    return {
        "po_number": extracted_data['po_number'],
        "po_date": extracted_data['po_date'],
        "po_data": extracted_data,
        "vendor_info": extracted_data['vendor_info'],
        "vendor_match": vendor_match,
        "line_items": extracted_data['line_items'],
        "line_item_count": len(extracted_data['line_items']),
        "subtotal": extracted_data['subtotal'],
        "total_amount": extracted_data['total_amount'],
        "extraction_confidence": round(overall_confidence, 3),
        "field_confidences": confidence_scores,
        "meets_confidence_threshold": overall_confidence >= confidence_threshold,
        "validation_results": validation_results,
        "validation_passed": all(v.get('valid', False) for v in validation_results.values()),
        "payment_terms": extracted_data['payment_terms'],
        "delivery_date": extracted_data['delivery_date'],
        "extracted_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "po_extract",
        "factory_version": "2.0.0",
        "context_keys_used": ["extraction_config", "po_validation", "supplier_config"]
    }


def _validate_po_data(data: Dict, rules: Dict) -> Dict[str, Dict]:
    """Validate extracted PO data."""
    results = {}

    # Validate PO number
    if rules.get('require_po_number', True):
        results['po_number'] = {
            'valid': bool(data.get('po_number')),
            'message': 'PO number present' if data.get('po_number') else 'Missing PO number'
        }

    # Validate vendor
    if rules.get('require_vendor', True):
        vendor = data.get('vendor_info', {})
        results['vendor'] = {
            'valid': bool(vendor.get('vendor_name')),
            'message': 'Vendor information present' if vendor.get('vendor_name') else 'Missing vendor'
        }

    # Validate line items
    line_items = data.get('line_items', [])
    max_items = rules.get('max_line_items', 100)
    results['line_items'] = {
        'valid': 0 < len(line_items) <= max_items,
        'message': f'{len(line_items)} line items' if line_items else 'No line items'
    }

    return results


def _validate_totals(data: Dict) -> bool:
    """Validate that line item totals match subtotal."""
    line_items = data.get('line_items', [])
    calculated_subtotal = sum(item.get('extended_price', 0) for item in line_items)
    stated_subtotal = data.get('subtotal', 0)

    return abs(calculated_subtotal - stated_subtotal) < 0.01


def _match_vendor(vendor_info: Dict, supplier_config: Dict) -> Dict:
    """Match vendor to known suppliers."""
    vendor_name = vendor_info.get('vendor_name', '').lower()
    known_vendors = supplier_config.get('known_vendors', {})

    for vendor_id, vendor_data in known_vendors.items():
        if vendor_data.get('name', '').lower() in vendor_name:
            return {
                'matched': True,
                'vendor_id': vendor_id,
                'vendor_data': vendor_data
            }

    return {
        'matched': False,
        'vendor_id': None,
        'suggestion': 'New vendor - may require setup'
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(po_extract(event))
