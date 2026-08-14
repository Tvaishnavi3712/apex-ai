"""
Invoice Extract Action
Extract structured data from invoices using Azure AI Document Intelligence
"""

import boto3
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


# Invoice Blueprint Schema
INVOICE_BLUEPRINT_SCHEMA = {
    "blueprintName": "apex-invoice-v1",
    "description": "Extract structured data from vendor invoices",
    "schema": {
        "vendor": {
            "name": {"type": "string", "description": "Vendor company name"},
            "address": {"type": "string", "description": "Vendor address"},
            "tax_id": {"type": "string", "description": "Vendor tax ID / EIN"},
            "phone": {"type": "string", "description": "Vendor phone number"},
            "email": {"type": "string", "description": "Vendor email"}
        },
        "invoice": {
            "number": {"type": "string", "description": "Invoice number"},
            "date": {"type": "string", "description": "Invoice date"},
            "due_date": {"type": "string", "description": "Payment due date"},
            "po_number": {"type": "string", "description": "Purchase order reference"},
            "terms": {"type": "string", "description": "Payment terms (NET30, etc.)"}
        },
        "bill_to": {
            "name": {"type": "string", "description": "Bill to company name"},
            "address": {"type": "string", "description": "Bill to address"},
            "attention": {"type": "string", "description": "Attention line"}
        },
        "line_items": {
            "type": "array",
            "items": {
                "description": {"type": "string"},
                "quantity": {"type": "number"},
                "unit_price": {"type": "number"},
                "amount": {"type": "number"},
                "item_code": {"type": "string"}
            }
        },
        "totals": {
            "subtotal": {"type": "number", "description": "Subtotal before tax"},
            "tax_rate": {"type": "number", "description": "Tax rate percentage"},
            "tax_amount": {"type": "number", "description": "Tax amount"},
            "shipping": {"type": "number", "description": "Shipping charges"},
            "discount": {"type": "number", "description": "Discount amount"},
            "total": {"type": "number", "description": "Total amount due"}
        },
        "payment": {
            "bank_name": {"type": "string", "description": "Bank name"},
            "account_number": {"type": "string", "description": "Bank account number"},
            "routing_number": {"type": "string", "description": "Bank routing number"},
            "swift_code": {"type": "string", "description": "SWIFT/BIC code"}
        }
    }
}


@apex_action(ApexActionSchema(
    name="invoice_extract",
    description="Extract structured data from invoice documents using BDA",
    category="document",
    industry="financial_services",
    input_schema=ActionInputSchema(description="Invoice extraction parameters")
        .add_string("document_s3_uri", "blob URI of the invoice document", required=True)
        .add_string("blueprint_arn", "BDA blueprint ARN (optional, uses default)", required=False)
        .add_string("output_s3_uri", "blob URI for extraction output", required=False)
        .add_boolean("wait_for_completion", "Wait for extraction to complete", required=False),
    output_schema=ActionOutputSchema(description="Invoice extraction result")
        .add_string("status", "Extraction status: initiated, processing, completed, failed")
        .add_string("invocation_arn", "BDA invocation ARN for tracking")
        .add_boolean("completed", "Whether extraction is complete")
))
def invoice_extract(
    document_s3_uri: str,
    blueprint_arn: str = None,
    output_s3_uri: str = None,
    wait_for_completion: bool = False
) -> dict:
    """
    Extract structured data from an invoice using Azure AI Document Intelligence

    Args:
        document_s3_uri: blob URI of the invoice (s3://bucket/key)
        blueprint_arn: Optional custom blueprint ARN
        output_s3_uri: Optional output location
        wait_for_completion: Whether to wait for extraction (sync mode)

    Returns:
        Extraction status and invocation details
    """
    bda_runtime = boto3.client('azure-document-intelligence')
    s3 = boto3.client('s3')

    region = os.environ.get('AWS_REGION', 'us-east-1')
    account_id = boto3.client('sts').get_caller_identity()['Account']

    # Default output location
    if not output_s3_uri:
        output_bucket = os.environ.get('DOCUMENTS_PROCESSED_BUCKET', 'apex-documents-processed')
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        output_s3_uri = f"s3://{output_bucket}/invoice-extractions/{timestamp}/"

    # Data automation profile ARN
    profile_arn = f"azure-resource-id"

    try:
        # Prepare request
        request = {
            'inputConfiguration': {
                's3Uri': document_s3_uri
            },
            'outputConfiguration': {
                's3Uri': output_s3_uri
            },
            'dataAutomationProfileArn': profile_arn
        }

        # Add blueprint if specified
        if blueprint_arn:
            request['blueprints'] = [{'blueprintArn': blueprint_arn}]

        # Invoke BDA
        response = bda_runtime.invoke_data_automation_async(**request)
        invocation_arn = response['invocationArn']

        result = {
            "status": "initiated",
            "invocation_arn": invocation_arn,
            "document_s3_uri": document_s3_uri,
            "output_s3_uri": output_s3_uri,
            "completed": False,
            "initiated_at": datetime.utcnow().isoformat()
        }

        # Optionally wait for completion
        if wait_for_completion:
            result = _wait_for_extraction(bda_runtime, invocation_arn, result)

        return result

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "document_s3_uri": document_s3_uri,
            "completed": False
        }


def _wait_for_extraction(bda_runtime, invocation_arn: str, result: dict, max_wait_seconds: int = 300) -> dict:
    """Wait for BDA extraction to complete"""
    import time

    start_time = time.time()
    poll_interval = 5  # seconds

    while time.time() - start_time < max_wait_seconds:
        try:
            status_response = bda_runtime.get_data_automation_status(
                invocationArn=invocation_arn
            )

            status = status_response.get('status', 'InProgress')

            if status == 'Success':
                result['status'] = 'completed'
                result['completed'] = True
                result['output_location'] = status_response.get('outputConfiguration', {}).get('s3Uri')
                result['completed_at'] = datetime.utcnow().isoformat()

                # Optionally fetch and include extracted data
                # This would require reading from S3

                return result

            elif status in ['ServiceError', 'ClientError']:
                result['status'] = 'failed'
                result['error'] = status_response.get('errorMessage', 'Unknown error')
                result['completed'] = False
                return result

            # Still in progress
            time.sleep(poll_interval)

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            return result

    # Timeout
    result['status'] = 'timeout'
    result['message'] = f'Extraction did not complete within {max_wait_seconds} seconds'
    return result


def get_extraction_result(invocation_arn: str) -> dict:
    """
    Get the result of a previously initiated extraction

    Args:
        invocation_arn: The invocation ARN from invoice_extract

    Returns:
        Extraction status and results if complete
    """
    bda_runtime = boto3.client('azure-document-intelligence')
    s3 = boto3.client('s3')

    try:
        status_response = bda_runtime.get_data_automation_status(
            invocationArn=invocation_arn
        )

        status = status_response.get('status', 'InProgress')

        if status == 'Success':
            output_uri = status_response.get('outputConfiguration', {}).get('s3Uri', '')

            # Parse output blob URI and fetch results
            if output_uri.startswith('s3://'):
                bucket, key = output_uri.replace('s3://', '').split('/', 1)

                # List result files
                result_files = s3.list_objects_v2(Bucket=bucket, Prefix=key)

                # Find and read the main result file
                for obj in result_files.get('Contents', []):
                    if obj['Key'].endswith('.json'):
                        response = s3.get_object(Bucket=bucket, Key=obj['Key'])
                        extracted_data = json.loads(response['Body'].read())

                        return {
                            "status": "completed",
                            "invocation_arn": invocation_arn,
                            "extracted_data": extracted_data,
                            "output_uri": output_uri
                        }

            return {
                "status": "completed",
                "invocation_arn": invocation_arn,
                "output_uri": output_uri,
                "message": "Results available at output URI"
            }

        elif status in ['ServiceError', 'ClientError']:
            return {
                "status": "failed",
                "invocation_arn": invocation_arn,
                "error": status_response.get('errorMessage', 'Unknown error')
            }

        else:
            return {
                "status": "processing",
                "invocation_arn": invocation_arn,
                "message": "Extraction still in progress"
            }

    except Exception as e:
        return {
            "status": "error",
            "invocation_arn": invocation_arn,
            "error": str(e)
        }


def handler(event, context):
    """Lambda entry point"""
    # Check if this is a status check or new extraction
    if 'invocation_arn' in event and 'document_s3_uri' not in event:
        return get_extraction_result(event['invocation_arn'])

    return invoice_extract(**event)
