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
    # Killer Features tables (spec: Apex_Killer_Features_Spec.docx)
    DYNAMODB_REVIEW_DECISIONS:     str = "apex-ai-platform-review-decisions"
    DYNAMODB_SIMULATOR_SCENARIOS:  str = "apex-ai-platform-simulator-scenarios"
    # STP Phase 2 tables — created by `seed_stp_demo.py`
    DYNAMODB_PIPELINES:            str = "apex-ai-platform-pipelines"
    DYNAMODB_REVIEW_QUEUE:         str = "apex-ai-platform-review-queue"
    # ApexSignal tables (spec: ApexSignal_ClaudeCode_Spec.docx + Apex_Master_Implementation_Spec.docx §4)
    DYNAMODB_PREDICTIVE_EVENTS:    str = "apex-ai-platform-predictive-events"
    DYNAMODB_SUPPLIERS:            str = "apex-ai-platform-suppliers"
    DYNAMODB_AGENT_AUDIT_LOG:      str = "apex-ai-platform-agent-audit-log"
    DYNAMODB_INVENTORY_BOM:        str = "apex-ai-platform-inventory-bom"
    DYNAMODB_PURCHASE_ORDERS:      str = "apex-ai-platform-purchase-orders"

    # SageMaker endpoint names (deployed by backend/scripts/deploy_sagemaker_endpoints.py)
    # ── Supply-chain ──
    SAGEMAKER_ENDPOINT_LEAD_TIME: str = "apex-signal-lead-time"
    SAGEMAKER_ENDPOINT_SUPPLIER:  str = "apex-signal-supplier"
    SAGEMAKER_ENDPOINT_STOCKOUT:  str = "apex-signal-stockout"
    SAGEMAKER_ENDPOINT_DEMAND:    str = "apex-signal-demand"
    # ── Verizon Far Edge ──
    # Deployed by backend/scripts/deploy_sagemaker_vz_endpoints.py
    SAGEMAKER_ENDPOINT_VZ_WAVE_RISK:        str = "apex-signal-vz-wave-risk"
    SAGEMAKER_ENDPOINT_VZ_SITE_CERT:        str = "apex-signal-vz-site-cert"
    SAGEMAKER_ENDPOINT_VZ_THERMAL_ANOMALY:  str = "apex-signal-vz-thermal-anomaly"
    # ── EPROD ──
    # Deployed by backend/scripts/deploy_sagemaker_eprod_endpoints.py
    SAGEMAKER_ENDPOINT_EPROD_VENDOR_DRIFT:     str = "apex-signal-eprod-vendor-drift"
    SAGEMAKER_ENDPOINT_EPROD_TARIFF_FORECAST:  str = "apex-signal-eprod-tariff-forecast"
    SAGEMAKER_ENDPOINT_EPROD_CONTRACT_EXPIRY:  str = "apex-signal-eprod-contract-expiry"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Cognito
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""

    # Atlassian JIRA Cloud (Verizon Far Edge cycle output)
    # Modelled here so pydantic-settings doesn't reject the env vars. The
    # actual JIRA client (backend/services/jira_client.py) reads these via
    # os.environ directly so it can be re-read on demand by Settings UI.
    JIRA_URL:           str = ""
    JIRA_EMAIL:         str = ""
    JIRA_TOKEN:         str = ""
    JIRA_PROJECT_KEY:   str = "APEXVZ"
    JIRA_MOCK_MODE:     str = "false"

    class Config:
        env_file = ".env"
        case_sensitive = True
        # Forward-compat: if more env vars get added to .env later, don't
        # blow up app boot — just ignore unknown keys.
        extra = "ignore"


settings = Settings()
