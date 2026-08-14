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

    # Azure
    AZURE_LOCATION: str = "eastus"
    AZURE_SUBSCRIPTION_ID: str = ""

    # ── Agent runtime ────────────────────────────────────────────────────
    # AZURE BUILD: agents run on Azure AI Foundry Agent Service. The FOUNDRY_AGENT_*
    # names are retained so ported call sites resolve, but they are unused here.
    AZURE_AI_PROJECT_ID: str = ""
    AZURE_AI_PROJECT_URL: str = ""
    AZURE_AI_PROJECT_ENDPOINT: str = ""
    AZURE_FOUNDRY_AGENTS: str = ""          # JSON map: apex agent id -> foundry agent id
    SUPERVISOR_AGENT_ID: str = ""

    # Azure AI Document Intelligence
    DOCINTEL_PROJECT_ID: str = ""
    DOCINTEL_MODEL_ID: str = ""

    # Azure OpenAI
    # AZURE BUILD: the model router uses Azure OpenAI deployments, not Azure OpenAI
    # model ids. Name retained for ported call sites; value is the deployment.
    AZURE_OPENAI_DEPLOYMENT_DEFAULT: str = "gpt-5.4"
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-5.4"

    # Blob containers
    CONTAINER_DOCUMENTS_INCOMING: str = "apex-documents-incoming"
    CONTAINER_DOCUMENTS_PROCESSED: str = "apex-documents-processed"
    CONTAINER_BLUEPRINTS: str = "apex-blueprints"
    CONTAINER_SYNTHETIC_DATA: str = "apex-synthetic-data"

    # Cosmos DB containers
    TABLE_PLAYBOOKS: str = "apex-ai-platform-playbooks"
    TABLE_AGENTS: str = "apex-ai-platform-agents"
    TABLE_BLUEPRINTS: str = "apex-ai-platform-blueprints"
    TABLE_ACTIONS: str = "apex-ai-platform-actions"
    TABLE_WORK_ITEMS: str = "apex-ai-platform-work-items"
    TABLE_SESSIONS: str = "apex-ai-platform-sessions"
    TABLE_AUDIT_LOGS: str = "apex-ai-platform-audit-logs"
    # Killer Features tables (spec: Apex_Killer_Features_Spec.docx)
    TABLE_REVIEW_DECISIONS:     str = "apex-ai-platform-review-decisions"
    TABLE_SIMULATOR_SCENARIOS:  str = "apex-ai-platform-simulator-scenarios"
    # STP Phase 2 tables — created by `seed_stp_demo.py`
    TABLE_PIPELINES:            str = "apex-ai-platform-pipelines"
    TABLE_REVIEW_QUEUE:         str = "apex-ai-platform-review-queue"
    # ApexSignal tables (spec: ApexSignal_ClaudeCode_Spec.docx + Apex_Master_Implementation_Spec.docx §4)
    TABLE_PREDICTIVE_EVENTS:    str = "apex-ai-platform-predictive-events"
    TABLE_SUPPLIERS:            str = "apex-ai-platform-suppliers"
    TABLE_AGENT_AUDIT_LOG:      str = "apex-ai-platform-agent-audit-log"
    TABLE_INVENTORY_BOM:        str = "apex-ai-platform-inventory-bom"
    TABLE_PURCHASE_ORDERS:      str = "apex-ai-platform-purchase-orders"

    # Azure ML online endpoint names
    # ── Supply-chain ──
    AZUREML_ENDPOINT_LEAD_TIME: str = "apex-signal-lead-time"
    AZUREML_ENDPOINT_SUPPLIER:  str = "apex-signal-supplier"
    AZUREML_ENDPOINT_STOCKOUT:  str = "apex-signal-stockout"
    AZUREML_ENDPOINT_DEMAND:    str = "apex-signal-demand"
    # ── Verizon Far Edge ──
    # Deployed by backend/scripts/deploy_azure_ml_vz_endpoints.py
    AZUREML_ENDPOINT_VZ_WAVE_RISK:        str = "apex-signal-vz-wave-risk"
    AZUREML_ENDPOINT_VZ_SITE_CERT:        str = "apex-signal-vz-site-cert"
    AZUREML_ENDPOINT_VZ_THERMAL_ANOMALY:  str = "apex-signal-vz-thermal-anomaly"
    # ── EPROD ──
    # Deployed by backend/scripts/deploy_azure_ml_eprod_endpoints.py
    AZUREML_ENDPOINT_EPROD_VENDOR_DRIFT:     str = "apex-signal-eprod-vendor-drift"
    AZUREML_ENDPOINT_EPROD_TARIFF_FORECAST:  str = "apex-signal-eprod-tariff-forecast"
    AZUREML_ENDPOINT_EPROD_CONTRACT_EXPIRY:  str = "apex-signal-eprod-contract-expiry"

    # CORS
    # Apex on Azure runs the frontend on :3002 (so it can coexist with the AWS build on :3000)
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3002",
        "http://localhost:8000",
        "http://localhost:8002",
    ]

    # Microsoft Entra ID
    ENTRA_TENANT_ID: str = ""
    ENTRA_CLIENT_ID: str = ""

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
