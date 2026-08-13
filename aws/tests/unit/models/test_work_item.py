"""
Unit tests for WorkItem models.
"""
import pytest
from datetime import datetime


class TestWorkItemModels:
    """Tests for WorkItem Pydantic models."""

    @pytest.mark.unit
    def test_work_item_base_valid(self):
        """Test creating valid WorkItemBase."""
        from backend.models.work_item import WorkItemBase

        item = WorkItemBase(
            type="invoice_review",
            priority="high",
            payload={"invoice_id": "inv-123", "amount": 15000}
        )

        assert item.type == "invoice_review"
        assert item.priority == "high"

    @pytest.mark.unit
    def test_work_item_statuses(self):
        """Test valid work item statuses."""
        from backend.models.work_item import WorkItem

        statuses = ["pending", "executing", "completed", "failed", "needs_review"]

        for status in statuses:
            item = WorkItem(
                work_item_id="wi-001",
                type="test",
                status=status,
                priority="normal",
                payload={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            assert item.status == status

    @pytest.mark.unit
    def test_work_item_priorities(self):
        """Test valid work item priorities."""
        from backend.models.work_item import WorkItem

        priorities = ["low", "normal", "high", "urgent"]

        for priority in priorities:
            item = WorkItem(
                work_item_id="wi-priority",
                type="test",
                status="pending",
                priority=priority,
                payload={},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            assert item.priority == priority

    @pytest.mark.unit
    def test_work_item_with_agent(self):
        """Test work item assigned to agent."""
        from backend.models.work_item import WorkItem

        item = WorkItem(
            work_item_id="wi-002",
            type="invoice_processing",
            status="executing",
            priority="high",
            assigned_agent="agent-001",
            payload={"invoice_id": "inv-456"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert item.assigned_agent == "agent-001"
        assert item.status == "executing"

    @pytest.mark.unit
    def test_work_item_with_result(self):
        """Test work item with execution result."""
        from backend.models.work_item import WorkItem, WorkItemResult

        result = WorkItemResult(
            status="success",
            output={"processed": True, "approval": "auto_approved"},
            confidence=0.95,
            execution_time_ms=1250
        )

        item = WorkItem(
            work_item_id="wi-003",
            type="approval",
            status="completed",
            priority="normal",
            payload={"amount": 5000},
            result=result,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert item.result.status == "success"
        assert item.result.confidence == 0.95

    @pytest.mark.unit
    def test_work_item_with_attachments(self):
        """Test work item with file attachments."""
        from backend.models.work_item import WorkItem

        item = WorkItem(
            work_item_id="wi-004",
            type="document_review",
            status="pending",
            priority="normal",
            payload={},
            attachments=[
                {"key": "invoice.pdf", "bucket": "documents", "size": 102400},
                {"key": "receipt.jpg", "bucket": "documents", "size": 51200}
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert len(item.attachments) == 2
        assert item.attachments[0]["key"] == "invoice.pdf"

    @pytest.mark.unit
    def test_work_item_source_tracking(self):
        """Test work item source tracking."""
        from backend.models.work_item import WorkItem

        item = WorkItem(
            work_item_id="wi-005",
            type="escalation",
            status="pending",
            priority="urgent",
            payload={},
            source="playbook",
            source_id="pb-invoice-001",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert item.source == "playbook"
        assert item.source_id == "rb-invoice-001"

    @pytest.mark.unit
    def test_work_item_execution_history(self):
        """Test work item with execution history."""
        from backend.models.work_item import WorkItem

        history = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "action": "created",
                "actor": "system"
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "action": "assigned",
                "actor": "agent-001"
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "action": "completed",
                "actor": "agent-001",
                "details": {"result": "approved"}
            }
        ]

        item = WorkItem(
            work_item_id="wi-006",
            type="approval",
            status="completed",
            priority="normal",
            payload={},
            execution_history=history,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert len(item.execution_history) == 3
        assert item.execution_history[-1]["action"] == "completed"


class TestWorkItemResult:
    """Tests for WorkItemResult model."""

    @pytest.mark.unit
    def test_result_success(self):
        """Test successful work item result."""
        from backend.models.work_item import WorkItemResult

        result = WorkItemResult(
            status="success",
            output={"invoice_data": {"number": "INV-001", "amount": 1500}},
            confidence=0.98
        )

        assert result.status == "success"
        assert result.confidence == 0.98

    @pytest.mark.unit
    def test_result_failure(self):
        """Test failed work item result."""
        from backend.models.work_item import WorkItemResult

        result = WorkItemResult(
            status="failure",
            error="Unable to process document: invalid format",
            error_code="INVALID_FORMAT"
        )

        assert result.status == "failure"
        assert "invalid format" in result.error

    @pytest.mark.unit
    def test_result_needs_review(self):
        """Test result requiring human review."""
        from backend.models.work_item import WorkItemResult

        result = WorkItemResult(
            status="needs_review",
            output={"extracted_data": {}},
            confidence=0.45,
            review_reason="Low confidence extraction"
        )

        assert result.status == "needs_review"
        assert result.confidence < 0.5
