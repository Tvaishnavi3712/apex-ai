"""
Document Classification Action
Uses Claude vision to analyze and classify documents, matching to appropriate blueprints
"""

import boto3
try:  # AZURE BUILD: Cosmos DB resource -> Cosmos DB shim
    from sdk.azure_data import get_table_resource
except ImportError:
    from ...sdk.azure_data import get_table_resource

try:  # AZURE BUILD: azure-openai -> Azure OpenAI shim
    from sdk.azure_llm import get_bedrock_runtime
except ImportError:
    from ...sdk.azure_llm import get_bedrock_runtime
import json
import base64
import os
from typing import List, Optional, Dict, Any
from io import BytesIO

# Import SDK
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema
from sdk.schemas import SchemaProperty, PropertyType


# Default document types and their descriptions
DEFAULT_DOCUMENT_TYPES = {
    "invoice": "Vendor invoices containing invoice number, line items, amounts, and payment details",
    "receipt": "Purchase receipts with merchant info, items purchased, and totals",
    "bank_statement": "Monthly bank statements showing transactions and balances",
    "purchase_order": "Purchase orders with PO number, items, quantities, and shipping info",
    "contract": "Legal contracts and agreements with terms, parties, and signatures",
    "resume": "CVs/resumes with work experience, education, and skills",
    "claim": "Insurance or medical claims with claim details and amounts",
    "bill_of_lading": "Shipping documents with cargo, carrier, and destination info",
    "packing_slip": "Package contents lists with items and quantities",
    "quality_inspection": "QC/inspection reports with test results and pass/fail status",
    "offer_letter": "Employment offer letters with position, salary, and benefits",
    "tax_form": "Tax-related forms like W-4, I-9, or W-9",
    "medical_record": "Patient medical records or clinical notes",
    "other": "Documents that don't match other categories"
}

# Map document types to industries for blueprint matching
DOCTYPE_INDUSTRY_MAP = {
    "invoice": "financial_services",
    "receipt": "retail",
    "bank_statement": "financial_services",
    "purchase_order": "manufacturing",
    "contract": "financial_services",
    "resume": "hr",
    "claim": "healthcare_payers",
    "bill_of_lading": "manufacturing",
    "packing_slip": "manufacturing",
    "quality_inspection": "manufacturing",
    "offer_letter": "hr",
    "tax_form": "hr",
    "medical_record": "healthcare_clinical"
}


@apex_action(ApexActionSchema(
    name="document_classify",
    description="Classify a document using AI vision to determine document type and match to appropriate blueprint",
    category="document_intelligence",
    industry="general",
    input_schema=ActionInputSchema(description="Document classification parameters")
        .add_string("document_s3_uri", "blob URI of the document to classify (s3://bucket/key)", required=True)
        .add_array(
            "candidate_blueprints",
            "Optional list of blueprint IDs to consider for matching",
            items=SchemaProperty(type=PropertyType.STRING, description="Blueprint ID"),
            required=False
        )
        .add_string("industry_hint", "Optional hint about expected industry", required=False),
    output_schema=ActionOutputSchema(description="Classification result")
        .add_string("document_type", "Detected document type")
        .add_string("blueprint_id", "Matched blueprint ID (if found)")
        .add_string("blueprint_name", "Matched blueprint name")
        .add_number("confidence", "Classification confidence 0-1")
        .add_string("reasoning", "Explanation for the classification")
        .add_string("industry", "Detected industry")
))
def document_classify(
    document_s3_uri: str,
    candidate_blueprints: List[str] = None,
    industry_hint: str = None
) -> dict:
    """
    Classify a document using Claude vision

    Args:
        document_s3_uri: blob URI of the document (s3://bucket/key)
        candidate_blueprints: Optional list of blueprint IDs to match against
        industry_hint: Optional hint about expected industry

    Returns:
        Classification result with document type, blueprint match, and confidence
    """
    # Initialize AWS clients
    s3 = boto3.client('s3')
    llm = get_bedrock_runtime()
    tables = get_table_resource()

    try:
        # Parse blob URI
        bucket, key = _parse_s3_uri(document_s3_uri)

        # Download document from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        document_bytes = response['Body'].read()
        content_type = response.get('ContentType', 'application/pdf')

        # Convert to base64 for Claude
        document_base64 = base64.standard_b64encode(document_bytes).decode('utf-8')

        # Determine media type for Claude
        media_type = _get_media_type(content_type, key)

        # Get available blueprints for context
        blueprints = _get_available_blueprints(cosmos_db, candidate_blueprints, industry_hint)

        # Build classification prompt
        prompt = _build_classification_prompt(blueprints, industry_hint)

        # Call Claude for classification
        model_id = os.environ.get('AZURE_OPENAI_DEPLOYMENT_DEFAULT', 'anthropic.claude-opus-4-5-20251101-v1:0')

        claude_response = llm.invoke_model(
            modelId=model_id,
            body=json.dumps({
                                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": document_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            })
        )

        # Parse Claude response
        result = json.loads(claude_response['body'].read())
        classification_text = result['content'][0]['text']

        # Extract structured classification from Claude's response
        classification = _parse_classification_response(classification_text)

        # Match to blueprint if not already matched
        if not classification.get('blueprint_id') and blueprints:
            matched = _match_blueprint(classification['document_type'], blueprints)
            if matched:
                classification['blueprint_id'] = matched['blueprint_id']
                classification['blueprint_name'] = matched['name']

        # Add industry if not detected
        if not classification.get('industry'):
            classification['industry'] = DOCTYPE_INDUSTRY_MAP.get(
                classification['document_type'],
                industry_hint or 'general'
            )

        return {
            "status": "success",
            **classification
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "document_type": "unknown",
            "confidence": 0.0
        }


def _parse_s3_uri(uri: str) -> tuple:
    """Parse blob URI into bucket and key"""
    if not uri.startswith('s3://'):
        raise ValueError(f"Invalid blob URI: {uri}")

    parts = uri[5:].split('/', 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid blob URI format: {uri}")

    return parts[0], parts[1]


def _get_media_type(content_type: str, key: str) -> str:
    """Determine media type for Claude vision"""
    # Check content type first
    if 'pdf' in content_type.lower():
        return 'application/pdf'
    elif 'png' in content_type.lower():
        return 'image/png'
    elif 'jpeg' in content_type.lower() or 'jpg' in content_type.lower():
        return 'image/jpeg'
    elif 'gif' in content_type.lower():
        return 'image/gif'
    elif 'webp' in content_type.lower():
        return 'image/webp'

    # Fall back to file extension
    ext = key.lower().split('.')[-1] if '.' in key else ''
    ext_map = {
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }

    return ext_map.get(ext, 'application/pdf')


def _get_available_blueprints(
    cosmos_db,
    candidate_ids: List[str] = None,
    industry: str = None
) -> List[Dict[str, Any]]:
    """Get available blueprints from Cosmos DB"""
    table_name = os.environ.get('BLUEPRINTS_TABLE', 'apex-blueprints')

    try:
        table = cosmos_db.Table(table_name)

        if candidate_ids:
            # Get specific blueprints
            blueprints = []
            for bid in candidate_ids:
                response = table.get_item(Key={'blueprint_id': bid})
                if 'Item' in response:
                    blueprints.append(response['Item'])
            return blueprints

        # Scan for blueprints (filtered by industry if specified)
        scan_kwargs = {'Limit': 50}
        if industry:
            scan_kwargs['FilterExpression'] = 'industry = :ind'
            scan_kwargs['ExpressionAttributeValues'] = {':ind': industry}

        response = table.scan(**scan_kwargs)
        return response.get('Items', [])

    except Exception as e:
        print(f"Error fetching blueprints: {e}")
        return []


def _build_classification_prompt(blueprints: List[Dict], industry_hint: str = None) -> str:
    """Build the classification prompt for Claude"""

    # Build document types section
    doc_types = "\n".join([
        f"- **{dtype}**: {desc}"
        for dtype, desc in DEFAULT_DOCUMENT_TYPES.items()
    ])

    # Build blueprints section if available
    blueprint_section = ""
    if blueprints:
        bp_list = "\n".join([
            f"- {bp.get('blueprint_id', 'unknown')}: {bp.get('name', '')} - {bp.get('description', '')[:100]}"
            for bp in blueprints[:20]  # Limit to 20 blueprints
        ])
        blueprint_section = f"""

## Available Blueprints
{bp_list}
"""

    industry_section = ""
    if industry_hint:
        industry_section = f"\nNote: The expected industry is **{industry_hint}**."

    return f"""Analyze this document image and classify it into the most appropriate document type.

## Document Types
{doc_types}
{blueprint_section}{industry_section}

## Instructions
1. Carefully examine the document structure, headers, and content
2. Identify key features that indicate the document type (e.g., "Invoice #", "Purchase Order", "Statement")
3. Select the most appropriate document type from the list above
4. If a matching blueprint exists, identify it
5. Provide a confidence score based on how clearly the document matches

## Response Format
Respond with a JSON object:
```json
{{
    "document_type": "the document type",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this classification was chosen",
    "blueprint_id": "matching blueprint ID if found",
    "blueprint_name": "matching blueprint name",
    "key_indicators": ["indicator1", "indicator2"],
    "industry": "detected industry"
}}
```

Only respond with the JSON object, no other text."""


def _parse_classification_response(response_text: str) -> Dict[str, Any]:
    """Parse Claude's classification response"""
    try:
        # Try to extract JSON from response
        # Handle potential markdown code blocks
        text = response_text.strip()
        if text.startswith('```'):
            # Remove markdown code block
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1])

        classification = json.loads(text)

        return {
            "document_type": classification.get('document_type', 'other'),
            "confidence": float(classification.get('confidence', 0.5)),
            "reasoning": classification.get('reasoning', ''),
            "blueprint_id": classification.get('blueprint_id'),
            "blueprint_name": classification.get('blueprint_name'),
            "industry": classification.get('industry'),
            "alternatives": []
        }

    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract key information
        return {
            "document_type": "other",
            "confidence": 0.3,
            "reasoning": response_text[:500],
            "blueprint_id": None,
            "blueprint_name": None,
            "industry": None,
            "alternatives": []
        }


def _match_blueprint(document_type: str, blueprints: List[Dict]) -> Optional[Dict]:
    """Match document type to a blueprint"""
    # Direct document_type match
    for bp in blueprints:
        if bp.get('document_type', '').lower() == document_type.lower():
            return bp

    # Partial name match
    for bp in blueprints:
        if document_type.lower() in bp.get('name', '').lower():
            return bp
        if document_type.lower() in bp.get('description', '').lower():
            return bp

    return None


# Lambda handler
def handler(event, context):
    """Lambda entry point"""
    return document_classify(**event)
