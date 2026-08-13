"""Apex service layer — Azure implementations."""

# Cloud adapters
from .cosmos import CosmosService, TableStore
from .blob import BlobService, ObjectStore
from .azure_openai import AzureOpenAIService, ModelRouter, get_model_router
from .azure_ml import AzureMLPredictor
from .foundry_agent import FoundryAgentService
from .doc_intelligence import DocumentIntelligenceService
from .queue import QueueService

# Platform services (cloud-neutral)
from .action_registry import ActionRegistry, get_registry, register_actions_to_db
from .virtual_fields import VirtualFieldsProcessor, process_virtual_fields
from .small_factory import SmallFactoryEngine, register_factory, get_factory_engine

__all__ = [
    "CosmosService", "TableStore",
    "BlobService", "ObjectStore",
    "AzureOpenAIService", "ModelRouter", "get_model_router",
    "AzureMLPredictor",
    "FoundryAgentService",
    "DocumentIntelligenceService",
    "QueueService",
    "ActionRegistry", "get_registry", "register_actions_to_db",
    "VirtualFieldsProcessor", "process_virtual_fields",
    "SmallFactoryEngine", "register_factory", "get_factory_engine",
]
