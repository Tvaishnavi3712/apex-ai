"""
Unit tests for Agent models.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError


class TestAgentModels:
    """Tests for Agent Pydantic models."""

    @pytest.mark.unit
    def test_agent_base_valid(self):
        """Test creating valid AgentBase."""
        from backend.models.agent import AgentBase

        agent = AgentBase(
            name="Invoice Agent",
            description="Processes invoices",
            type="worker",
            model_id="anthropic.claude-3-sonnet"
        )

        assert agent.name == "Invoice Agent"
        assert agent.type == "worker"

    @pytest.mark.unit
    def test_agent_types(self):
        """Test valid agent types."""
        from backend.models.agent import AgentBase

        valid_types = ["supervisor", "collaborator", "worker"]

        for agent_type in valid_types:
            agent = AgentBase(
                name="Test Agent",
                description="Test",
                type=agent_type,
                model_id="anthropic.claude-3-sonnet"
            )
            assert agent.type == agent_type

    @pytest.mark.unit
    def test_agent_status_values(self):
        """Test agent status values."""
        from backend.models.agent import Agent

        valid_statuses = ["draft", "deploying", "active", "failed", "archived"]

        for status in valid_statuses:
            agent = Agent(
                agent_id="agent-001",
                name="Test",
                description="Test",
                type="worker",
                status=status,
                environment="development",
                model_id="anthropic.claude-3-sonnet",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            assert agent.status == status

    @pytest.mark.unit
    def test_agent_with_action_groups(self):
        """Test agent with action group associations."""
        from backend.models.agent import Agent

        agent = Agent(
            agent_id="agent-002",
            name="Full Agent",
            description="Agent with actions",
            type="worker",
            status="active",
            environment="production",
            model_id="anthropic.claude-3-sonnet",
            action_group_ids=["ag-001", "ag-002", "ag-003"],
            knowledge_base_ids=["kb-001"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert len(agent.action_group_ids) == 3
        assert len(agent.knowledge_base_ids) == 1

    @pytest.mark.unit
    def test_agent_azure_openai_references(self):
        """Test agent with Azure OpenAI references."""
        from backend.models.agent import Agent

        agent = Agent(
            agent_id="agent-003",
            name="Deployed Agent",
            description="Deployed to Azure OpenAI",
            type="supervisor",
            status="active",
            environment="production",
            model_id="anthropic.claude-3-sonnet",
            foundry_agent_id="ABCD1234",
            foundry_agent_resource_id="azure-resource-id",
            azure_openai_alias_id="TSTALIASID",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert agent.foundry_agent_id == "ABCD1234"
        assert "azure-resource-id" in agent.foundry_agent_resource_id

    @pytest.mark.unit
    def test_supervisor_with_collaborators(self):
        """Test supervisor agent with collaborator associations."""
        from backend.models.agent import Agent

        agent = Agent(
            agent_id="supervisor-001",
            name="Main Supervisor",
            description="Orchestrates collaborators",
            type="supervisor",
            status="active",
            environment="development",
            model_id="anthropic.claude-3-sonnet",
            collaborator_ids=["agent-001", "agent-002"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert agent.type == "supervisor"
        assert len(agent.collaborator_ids) == 2

    @pytest.mark.unit
    def test_agent_metrics(self):
        """Test agent with invocation metrics."""
        from backend.models.agent import Agent

        agent = Agent(
            agent_id="agent-004",
            name="Metrics Agent",
            description="Has metrics",
            type="worker",
            status="active",
            environment="production",
            model_id="anthropic.claude-3-sonnet",
            invocation_count=150,
            avg_latency_ms=1250.5,
            error_count=3,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert agent.invocation_count == 150
        assert agent.avg_latency_ms == 1250.5
        assert agent.error_count == 3

    @pytest.mark.unit
    def test_agent_create_model(self):
        """Test AgentCreate model."""
        from backend.models.agent import AgentCreate

        agent = AgentCreate(
            name="New Agent",
            description="Fresh agent",
            type="worker",
            model_id="anthropic.claude-3-sonnet",
            action_group_ids=["ag-001"],
            environment="development"
        )

        assert agent.name == "New Agent"
        assert agent.environment == "development"

    @pytest.mark.unit
    def test_agent_update_partial(self):
        """Test AgentUpdate allows partial updates."""
        from backend.models.agent import AgentUpdate

        update = AgentUpdate(
            description="Updated description only"
        )

        assert update.description == "Updated description only"
        assert update.name is None


class TestAgentEnvironments:
    """Tests for agent environment configurations."""

    @pytest.mark.unit
    def test_valid_environments(self):
        """Test valid environment values."""
        from backend.models.agent import Agent

        environments = ["development", "staging", "production"]

        for env in environments:
            agent = Agent(
                agent_id="env-agent",
                name="Test",
                description="Test",
                type="worker",
                status="active",
                environment=env,
                model_id="anthropic.claude-3-sonnet",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            assert agent.environment == env
