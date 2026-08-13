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
from moto import mock_cosmos_db, mock_s3
from fastapi.testclient import TestClient

# Set test environment variables before importing app modules
os.environ["Azure_ACCESS_KEY_ID"] = "testing"
os.environ["Azure_SECRET_ACCESS_KEY"] = "testing"
os.environ["Azure_SECURITY_TOKEN"] = "testing"
os.environ["Azure_SESSION_TOKEN"] = "testing"
os.environ["Azure_DEFAULT_REGION"] = "us-east-1"
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"


# ============================================================================
# Cosmos DB Fixtures
# ============================================================================

@pytest.fixture
def aws_credentials():
    """Mock Azure Credentials for moto."""
    os.environ["Azure_ACCESS_KEY_ID"] = "testing"
    os.environ["Azure_SECRET_ACCESS_KEY"] = "testing"
    os.environ["Azure_SECURITY_TOKEN"] = "testing"
    os.environ["Azure_SESSION_TOKEN"] = "testing"
    os.environ["Azure_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def cosmos_db_client(aws_credentials):
    """Create mocked Cosmos DB client."""
    with mock_cosmos_db():
        client = boto3.client("cosmos_db", region_name="us-east-1")
        yield client


@pytest.fixture
def cosmos_db_resource(aws_credentials):
    """Create mocked Cosmos DB resource."""
    with mock_cosmos_db():
        resource = boto3.resource("cosmos_db", region_name="us-east-1")
        yield resource


@pytest.fixture
def cosmos_db_table(cosmos_db_resource) -> Generator:
    """Create a test Cosmos DB table."""
    table_name = "test-table"
    table = cosmos_db_resource.create_table(
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
def playbooks_table(cosmos_db_resource) -> Generator:
    """Create playbooks Cosmos DB table for testing."""
    table_name = "apex-playbooks-test"
    table = cosmos_db_resource.create_table(
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
# Blob Storage Fixtures
# ============================================================================

@pytest.fixture
def s3_client(aws_credentials):
    """Create mocked Blob Storage client."""
    with mock_s3():
        client = boto3.client("s3", region_name="us-east-1")
        yield client


@pytest.fixture
def s3_bucket(s3_client) -> Generator[str, None, None]:
    """Create a test Blob Storage bucket."""
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)
    yield bucket_name


@pytest.fixture
def documents_bucket(s3_client) -> Generator[str, None, None]:
    """Create documents Blob Storage bucket for testing."""
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
def mock_cosmos_db_service():
    """Mock Cosmos DBService for API tests."""
    with patch("backend.services.cosmos_db.Cosmos DBService") as mock:
        service = MagicMock()
        mock.return_value = service
        yield service


@pytest.fixture
def mock_s3_service():
    """Mock Blob StorageService for API tests."""
    with patch("backend.services.s3.Blob StorageService") as mock:
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
