"""AWS service integrations"""
from .dynamodb import DynamoDBService
from .s3 import S3Service
from .action_registry import ActionRegistry, get_registry, register_actions_to_db
from .virtual_fields import VirtualFieldsProcessor, process_virtual_fields
from .sqs import SQSService
from .small_factory import SmallFactoryEngine, register_factory, get_factory_engine
from .bedrock_claude import BedrockClaudeService, get_bedrock_claude_service
from .agentcore import AgentCoreService
