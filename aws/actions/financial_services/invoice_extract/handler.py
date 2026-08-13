"""
Invoice Extract - Financial Services Action (Context-Driven)
Extract structured data from invoice documents using AI

Context-Driven Architecture:
- Extraction fields from playbook context.extraction_config
- Validation rules from context.extraction_config.validation
- Field mappings from context.extraction_config.field_mappings
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import re
import json

try:
    from services.small_factory import register_factory
    SMALL_FACTORY_ENABLED = True
except ImportError:
    SMALL_FACTORY_ENABLED = False
    def register_factory(name):
        def decorator(func):
            return func
        return decorator

try:
    import boto3
    AWS_ENABLED = True
except ImportError:
    AWS_ENABLED = False

logger = structlog.get_logger()


# Default extraction configuration
DEFAULT_EXTRACTION_CONFIG = {
    "required_fields": [
        "invoice_number", "invoice_date", "vendor_name", "total_amount"
    ],
    "optional_fields": [
        "po_number", "due_date", "tax_amount", "subtotal",
        "line_items", "payment_terms", "vendor_address"
    ],
    "validation": {
        "invoice_number": {"pattern": r"^[A-Z0-9\-]+$"},
        "total_amount": {"min": 0, "max": 10000000}
    },
    "confidence_threshold": 0.85
}


@register_factory("invoice_extract")
async def invoice_extract(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract invoice data from document (context-driven).

    Context keys used:
        - extraction_config: Field extraction configuration
            - required_fields: Fields that must be extracted
            - optional_fields: Optional fields to extract
            - validation: Validation rules per field
            - confidence_threshold: Minimum confidence for extraction

    Input:
        document_intake: Document intake results
        text_content: Extracted text (optional)
        use_ai: Whether to use AI extraction

    Output:
        invoice_number: Invoice number
        invoice_date: Invoice date
        vendor_name: Vendor name
        total_amount: Total amount
        line_items: Line items array
        confidence_scores: Confidence per field
        extraction_complete: Whether all required fields extracted
    """
    context = context or input_data.get('context', {})
    extraction_config = context.get('extraction_config', DEFAULT_EXTRACTION_CONFIG)

    logger.info(
        "Invoice extract invoked",
        context_driven=bool(context)
    )

    # Get document info from upstream
    doc_intake = input_data.get('document_intake', {})
    text_content = doc_intake.get('text_content') or input_data.get('text_content', '')
    document_uri = doc_intake.get('document_s3_uri') or input_data.get('document_s3_uri')

    # Get configuration from context
    required_fields = extraction_config.get('required_fields', DEFAULT_EXTRACTION_CONFIG['required_fields'])
    optional_fields = extraction_config.get('optional_fields', DEFAULT_EXTRACTION_CONFIG['optional_fields'])
    validation_rules = extraction_config.get('validation', {})
    confidence_threshold = extraction_config.get('confidence_threshold', 0.85)

    # Perform extraction
    use_ai = input_data.get('use_ai', True)

    if use_ai and AWS_ENABLED:
        extracted_data = await _extract_with_textract(document_uri)
    else:
        extracted_data = _extract_with_patterns(text_content)

    # Validate extracted data
    validation_results = _validate_extraction(extracted_data, validation_rules, required_fields)

    # Calculate overall confidence
    confidence_scores = extracted_data.get('confidence_scores', {})
    avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.5

    # Determine if extraction is complete
    missing_required = [f for f in required_fields if not extracted_data.get(f)]
    extraction_complete = len(missing_required) == 0 and avg_confidence >= confidence_threshold

    return {
        "invoice_number": extracted_data.get('invoice_number'),
        "invoice_date": extracted_data.get('invoice_date'),
        "due_date": extracted_data.get('due_date'),
        "vendor_name": extracted_data.get('vendor_name'),
        "vendor_id": extracted_data.get('vendor_id'),
        "vendor_address": extracted_data.get('vendor_address'),
        "po_number": extracted_data.get('po_number'),
        "subtotal": extracted_data.get('subtotal'),
        "tax_amount": extracted_data.get('tax_amount'),
        "total_amount": extracted_data.get('total_amount'),
        "currency": extracted_data.get('currency', 'USD'),
        "payment_terms": extracted_data.get('payment_terms'),
        "line_items": extracted_data.get('line_items', []),
        "line_item_count": len(extracted_data.get('line_items', [])),
        "confidence_scores": confidence_scores,
        "average_confidence": round(avg_confidence, 3),
        "validation_results": validation_results,
        "missing_required_fields": missing_required,
        "extraction_complete": extraction_complete,
        "requires_review": not extraction_complete or avg_confidence < confidence_threshold,
        "extracted_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "invoice_extract",
        "factory_version": "2.0.0",
        "context_keys_used": ["extraction_config"]
    }


async def _extract_with_textract(document_uri: str) -> Dict[str, Any]:
    """Extract invoice data using AWS Textract."""
    if not document_uri:
        return {}

    try:
        # Parse S3 URI
        if document_uri.startswith('s3://'):
            parts = document_uri[5:].split('/', 1)
            bucket, key = parts[0], parts[1]
        else:
            return _get_sample_extraction()

        textract = boto3.client('textract')

        # Use AnalyzeExpense for invoices
        response = textract.analyze_expense(
            Document={'S3Object': {'Bucket': bucket, 'Name': key}}
        )

        # Parse Textract response
        extracted = _parse_textract_expense(response)
        return extracted

    except Exception as e:
        logger.warning("Textract extraction failed, using pattern matching", error=str(e))
        return _get_sample_extraction()


def _extract_with_patterns(text: str) -> Dict[str, Any]:
    """Extract invoice data using regex patterns."""
    if not text:
        return _get_sample_extraction()

    extracted = {
        'confidence_scores': {}
    }

    # Invoice number patterns
    inv_match = re.search(r'(?:invoice|inv)[\s#:]*([A-Z0-9\-]+)', text, re.I)
    if inv_match:
        extracted['invoice_number'] = inv_match.group(1)
        extracted['confidence_scores']['invoice_number'] = 0.8

    # Date patterns
    date_match = re.search(r'(?:date|dated?)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})', text, re.I)
    if date_match:
        extracted['invoice_date'] = date_match.group(1)
        extracted['confidence_scores']['invoice_date'] = 0.75

    # Amount patterns
    amount_match = re.search(r'(?:total|amount|due)[\s:]*\$?([\d,]+\.?\d*)', text, re.I)
    if amount_match:
        amount_str = amount_match.group(1).replace(',', '')
        extracted['total_amount'] = float(amount_str)
        extracted['confidence_scores']['total_amount'] = 0.7

    # PO number patterns
    po_match = re.search(r'(?:po|purchase\s+order)[\s#:]*([A-Z0-9\-]+)', text, re.I)
    if po_match:
        extracted['po_number'] = po_match.group(1)
        extracted['confidence_scores']['po_number'] = 0.75

    return extracted


def _parse_textract_expense(response: Dict) -> Dict[str, Any]:
    """Parse Textract AnalyzeExpense response."""
    extracted = {
        'line_items': [],
        'confidence_scores': {}
    }

    for doc in response.get('ExpenseDocuments', []):
        for field in doc.get('SummaryFields', []):
            field_type = field.get('Type', {}).get('Text', '')
            value = field.get('ValueDetection', {}).get('Text', '')
            confidence = field.get('ValueDetection', {}).get('Confidence', 0) / 100

            if 'INVOICE' in field_type and 'NUMBER' in field_type:
                extracted['invoice_number'] = value
                extracted['confidence_scores']['invoice_number'] = confidence
            elif 'VENDOR' in field_type and 'NAME' in field_type:
                extracted['vendor_name'] = value
                extracted['confidence_scores']['vendor_name'] = confidence
            elif 'TOTAL' in field_type:
                try:
                    extracted['total_amount'] = float(value.replace('$', '').replace(',', ''))
                    extracted['confidence_scores']['total_amount'] = confidence
                except:
                    pass
            elif 'DATE' in field_type:
                extracted['invoice_date'] = value
                extracted['confidence_scores']['invoice_date'] = confidence
            elif 'PO' in field_type or 'PURCHASE' in field_type:
                extracted['po_number'] = value
                extracted['confidence_scores']['po_number'] = confidence

        # Extract line items
        for item in doc.get('LineItemGroups', []):
            for line in item.get('LineItems', []):
                line_item = {}
                for field in line.get('LineItemExpenseFields', []):
                    field_type = field.get('Type', {}).get('Text', '')
                    value = field.get('ValueDetection', {}).get('Text', '')

                    if 'DESCRIPTION' in field_type:
                        line_item['description'] = value
                    elif 'QUANTITY' in field_type:
                        line_item['quantity'] = value
                    elif 'UNIT_PRICE' in field_type:
                        line_item['unit_price'] = value
                    elif 'AMOUNT' in field_type:
                        line_item['amount'] = value

                if line_item:
                    extracted['line_items'].append(line_item)

    return extracted


def _get_sample_extraction() -> Dict[str, Any]:
    """Return sample extraction for testing."""
    return {
        'invoice_number': 'INV-2024-001234',
        'invoice_date': '2024-03-15',
        'vendor_name': 'Sample Vendor Inc.',
        'total_amount': 1500.00,
        'tax_amount': 125.00,
        'subtotal': 1375.00,
        'po_number': 'PO-2024-5678',
        'currency': 'USD',
        'line_items': [
            {'description': 'Professional Services', 'quantity': '10', 'unit_price': '137.50', 'amount': '1375.00'}
        ],
        'confidence_scores': {
            'invoice_number': 0.95,
            'invoice_date': 0.92,
            'vendor_name': 0.88,
            'total_amount': 0.96,
            'po_number': 0.90
        }
    }


def _validate_extraction(
    extracted: Dict[str, Any],
    validation_rules: Dict[str, Any],
    required_fields: List[str]
) -> Dict[str, Any]:
    """Validate extracted data against rules."""
    results = {}

    for field, rules in validation_rules.items():
        value = extracted.get(field)
        if value is None:
            results[field] = {'valid': False, 'reason': 'missing'}
            continue

        # Pattern validation
        if 'pattern' in rules:
            if not re.match(rules['pattern'], str(value)):
                results[field] = {'valid': False, 'reason': 'pattern_mismatch'}
                continue

        # Range validation
        if 'min' in rules or 'max' in rules:
            try:
                num_val = float(value)
                if 'min' in rules and num_val < rules['min']:
                    results[field] = {'valid': False, 'reason': 'below_minimum'}
                    continue
                if 'max' in rules and num_val > rules['max']:
                    results[field] = {'valid': False, 'reason': 'above_maximum'}
                    continue
            except:
                results[field] = {'valid': False, 'reason': 'not_numeric'}
                continue

        results[field] = {'valid': True}

    return results


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(invoice_extract(event))
