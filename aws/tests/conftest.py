"""
Pytest configuration and shared fixtures for Apex AI Platform tests.
"""
import os
import json
import pytest
from datetime import datetime
from decimal import Decimal
from typing import Generator, Dict, Any
from unittest.mock import MagicMock, patch

import boto3
from moto import mock_dynamodb, mock_s3
from fastapi.testclient import TestClient

# Set test environment variables before importing app modules
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"


# ============================================================================
# DynamoDB Fixtures
# ============================================================================

@pytest.fixture
def aws_credentials():
    """Mock AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def dynamodb_client(aws_credentials):
    """Create mocked DynamoDB client."""
    with mock_dynamodb():
        client = boto3.client("dynamodb", region_name="us-east-1")
        yield client


@pytest.fixture
def dynamodb_resource(aws_credentials):
    """Create mocked DynamoDB resource."""
    with mock_dynamodb():
        resource = boto3.resource("dynamodb", region_name="us-east-1")
        yield resource


@pytest.fixture
def dynamodb_table(dynamodb_resource) -> Generator:
    """Create a test DynamoDB table."""
    table_name = "test-table"
    table = dynamodb_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "status", "AttributeType": "S"},
            {"AttributeName": "industry", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "status-index",
                "KeySchema": [{"AttributeName": "status", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "industry-status-index",
                "KeySchema": [
                    {"AttributeName": "industry", "KeyType": "HASH"},
                    {"AttributeName": "status", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.meta.client.get_waiter("table_exists").wait(TableName=table_name)
    yield table


@pytest.fixture
def playbooks_table(dynamodb_resource) -> Generator:
    """Create playbooks DynamoDB table for testing."""
    table_name = "apex-playbooks-test"
    table = dynamodb_resource.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "playbook_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "playbook_id", "AttributeType": "S"},
            {"AttributeName": "industry", "AttributeType": "S"},
            {"AttributeName": "status", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "industry-status-index",
                "KeySchema": [
                    {"AttributeName": "industry", "KeyType": "HASH"},
                    {"AttributeName": "status", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.meta.client.get_waiter("table_exists").wait(TableName=table_name)
    yield table


# ============================================================================
# S3 Fixtures
# ============================================================================

@pytest.fixture
def s3_client(aws_credentials):
    """Create mocked S3 client."""
    with mock_s3():
        client = boto3.client("s3", region_name="us-east-1")
        yield client


@pytest.fixture
def s3_bucket(s3_client) -> Generator[str, None, None]:
    """Create a test S3 bucket."""
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)
    yield bucket_name


@pytest.fixture
def documents_bucket(s3_client) -> Generator[str, None, None]:
    """Create documents S3 bucket for testing."""
    bucket_name = "apex-documents-incoming-test"
    s3_client.create_bucket(Bucket=bucket_name)
    yield bucket_name


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_playbook() -> Dict[str, Any]:
    """Sample playbook data for testing."""
    return {
        "playbook_id": "pb-001",
        "name": "Invoice Processing",
        "description": "Process vendor invoices automatically",
        "version": "1.0.0",
        "status": "active",
        "industry": "financial_services",
        "category": "accounts_payable",
        "intent": "Process incoming vendor invoices",
        "recipe": "1. Extract invoice data\n2. Validate vendor\n3. Route for approval",
        "actions": ["invoice_extract", "vendor_lookup", "approval_route"],
        "triggers": [{"type": "s3_event", "bucket": "invoices"}],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "created_by": "test-user",
    }


@pytest.fixture
def sample_agent() -> Dict[str, Any]:
    """Sample agent data for testing."""
    return {
        "agent_id": "agent-001",
        "name": "Invoice Agent",
        "description": "Processes invoices using AI",
        "type": "worker",
        "status": "active",
        "environment": "development",
        "model_id": "anthropic.claude-3-sonnet",
        "action_group_ids": ["ag-001", "ag-002"],
        "knowledge_base_ids": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_blueprint() -> Dict[str, Any]:
    """Sample blueprint data for testing."""
    return {
        "blueprint_id": "bp-001",
        "name": "Invoice Blueprint",
        "description": "Extract invoice fields",
        "document_type": "invoice",
        "industry": "financial_services",
        "stage": "LIVE",
        "schema": {
            "class": "Invoice",
            "properties": {
                "invoice_number": {"type": "string"},
                "total_amount": {"type": "number"},
            },
        },
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_action() -> Dict[str, Any]:
    """Sample action data for testing."""
    return {
        "action_id": "action-001",
        "name": "vendor_lookup",
        "description": "Look up vendor information",
        "type": "lambda",
        "category": "data_lookup",
        "industry": "financial_services",
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor_name": {"type": "string"},
                "vendor_id": {"type": "string"},
            },
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "vendor": {"type": "object"},
                "status": {"type": "string"},
            },
        },
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_work_item() -> Dict[str, Any]:
    """Sample work item data for testing."""
    return {
        "work_item_id": "wi-001",
        "type": "invoice_review",
        "status": "pending",
        "priority": "high",
        "assigned_agent": "agent-001",
        "payload": {
            "invoice_id": "inv-123",
            "amount": 15000.00,
            "vendor": "Acme Corp",
        },
        "source": "playbook",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


# ============================================================================
# FastAPI Test Client
# ============================================================================

@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create FastAPI test client with mocked dependencies."""
    # Import here to avoid circular imports
    from backend.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_dynamodb_service():
    """Mock DynamoDBService for API tests."""
    with patch("backend.services.dynamodb.DynamoDBService") as mock:
        service = MagicMock()
        mock.return_value = service
        yield service


@pytest.fixture
def mock_s3_service():
    """Mock S3Service for API tests."""
    with patch("backend.services.s3.S3Service") as mock:
        service = MagicMock()
        mock.return_value = service
        yield service


# ============================================================================
# Utility Functions
# ============================================================================

def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


@pytest.fixture
def json_encoder():
    """JSON encoder that handles Decimal types."""
    return decimal_to_float
