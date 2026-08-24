"""
Configuration management for Apex AI Platform
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_ACCOUNT_ID: str = ""

    # Bedrock AgentCore
    AGENTCORE_GATEWAY_ID: str = ""
    AGENTCORE_GATEWAY_URL: str = ""
    SUPERVISOR_AGENT_ID: str = ""

    # Bedrock Data Automation
    BDA_PROJECT_ARN: str = ""
    BDA_PROFILE_ARN: str = ""

    # Bedrock Claude Model
    BEDROCK_CLAUDE_MODEL_ID: str = "us.anthropic.claude-opus-4-6-v1"

    # S3 Buckets
    S3_DOCUMENTS_INCOMING: str = "apex-documents-incoming"
    S3_DOCUMENTS_PROCESSED: str = "apex-documents-processed"
    S3_BLUEPRINTS: str = "apex-blueprints"
    S3_SYNTHETIC_DATA: str = "apex-synthetic-data"

    # DynamoDB Tables (matching deployed AWS tables)
    DYNAMODB_PLAYBOOKS: str = "apex-ai-platform-playbooks"
    DYNAMODB_AGENTS: str = "apex-ai-platform-agents"
    DYNAMODB_BLUEPRINTS: str = "apex-ai-platform-blueprints"
    DYNAMODB_ACTIONS: str = "apex-ai-platform-actions"
    DYNAMODB_WORK_ITEMS: str = "apex-ai-platform-work-items"
    DYNAMODB_SESSIONS: str = "apex-ai-platform-sessions"
    DYNAMODB_AUDIT_LOGS: str = "apex-ai-platform-audit-logs"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Cognito
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""

    # Atlassian JIRA Cloud
    JIRA_URL: str = ""
    JIRA_EMAIL: str = ""
    JIRA_TOKEN: str = ""
    JIRA_PROJECT_KEY: str = ""
    JIRA_MOCK_MODE: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# On networks with a TLS-inspecting proxy (e.g. corporate MITM firewalls),
# botocore's bundled certifi CA bundle won't trust the proxy's injected cert.
# Point boto3 at a combined bundle if one has been generated locally
# (see aws/backend/.certs/README.md) without forcing it on every machine.
_corp_ca_bundle = os.path.join(os.path.dirname(__file__), "..", ".certs", "combined-ca-bundle.pem")
if os.path.isfile(_corp_ca_bundle) and "AWS_CA_BUNDLE" not in os.environ:
    os.environ["AWS_CA_BUNDLE"] = os.path.abspath(_corp_ca_bundle)
