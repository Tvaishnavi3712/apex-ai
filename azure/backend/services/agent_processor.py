"""
Agent Processor Service
Handles end-to-end document processing workflow with status progression:
Pending → Processing → Extracting → Analyzing → Decision → Requires Approval/Completed

This simulates how Azure AI Foundry Agent Service would process documents through an agentic workflow.
"""

import asyncio
import uuid
import random
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from decimal import Decimal
import structlog

from services.cosmos import CosmosService
from core.config import settings

logger = structlog.get_logger()


def convert_floats_to_decimal(obj: Any) -> Any:
    """Convert all floats to Decimal for Cosmos DB compatibility"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    return obj


class ProcessingStage(str, Enum):
    """Detailed processing stages for visibility"""
    PENDING = "pending"
    QUEUED = "queued"
    EXTRACTING = "extracting"
    VALIDATING = "validating"
    ANALYZING_RISK = "analyzing_risk"
    CALCULATING_PREMIUM = "calculating_premium"
    CHECKING_LOSS_HISTORY = "checking_loss_history"
    MAKING_DECISION = "making_decision"
    REQUIRES_APPROVAL = "requires_approval"
    APPROVED = "approved"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentProcessorService:
    """
    Simulates agentic document processing workflow.
    In production, this would call actual Azure AI Foundry Agent Service.
    """

    # Sample CRE submission data for demo
    SAMPLE_SUBMISSIONS = [
        {
            "submission_id": "CRE-2026-001-MUP",
            "property_name": "Lakefront Development LLC - Mixed-Use Portfolio",
            "property_type": "Mixed-Use High-Rise",
            "location": "Chicago, IL",
            "tiv": 226000000,
            "risk_score": 72,
            "premium": 645000,
            "decision": "approve_with_conditions",
            "decision_text": "Refer to Senior Underwriter",
            "requires_approval": True,
            "approval_reason": "TIV exceeds $100M threshold",
        },
        {
            "submission_id": "CRE-2026-002-IND",
            "property_name": "Midwest Industrial Partners - Industrial Portfolio",
            "property_type": "Industrial/Warehouse",
            "location": "Multiple Midwest locations",
            "tiv": 372300000,
            "risk_score": 68,
            "premium": 892000,
            "decision": "approve_with_conditions",
            "decision_text": "Refer to Senior Underwriter",
            "requires_approval": True,
            "approval_reason": "Cold storage ammonia systems require specialist review",
        },
        {
            "submission_id": "CRE-2026-003-HRT",
            "property_name": "Coastal Hospitality Holdings - Hotels & Retail",
            "property_type": "Hospitality & Retail",
            "location": "Miami, FL",
            "tiv": 505000000,
            "risk_score": 52,
            "premium": 2150000,
            "decision": "refer_to_manager",
            "decision_text": "Refer to Underwriting Manager",
            "requires_approval": True,
            "approval_reason": "High risk score, hurricane exposure, open claims",
        },
    ]

    def __init__(self):
        self.db = CosmosService(settings.TABLE_WORK_ITEMS)
        self._processing_tasks: Dict[str, asyncio.Task] = {}
        self._status_callbacks: Dict[str, List[Callable]] = {}

    async def start_processing(self, work_item_id: str) -> Dict[str, Any]:
        """
        Start processing a work item through the agentic pipeline.
        Returns immediately with task info - processing happens async.
        """
        # Check if already processing
        if work_item_id in self._processing_tasks:
            return {
                "status": "already_processing",
                "work_item_id": work_item_id,
                "message": "This work item is already being processed"
            }

        # Get the work item
        work_item = await self.db.get_item({"work_item_id": work_item_id})
        if not work_item:
            return {
                "status": "error",
                "message": f"Work item {work_item_id} not found"
            }

        # Start async processing with error callback
        task = asyncio.create_task(self._process_work_item(work_item_id, work_item))
        self._processing_tasks[work_item_id] = task

        # Add callback to log any unhandled exceptions
        def on_task_done(t):
            try:
                exc = t.exception()
                if exc:
                    logger.error(f"Task failed for {work_item_id}: {exc}")
                    print(f"TASK EXCEPTION for {work_item_id}: {exc}")
                    traceback.print_exception(type(exc), exc, exc.__traceback__)
            except asyncio.CancelledError:
                pass

        task.add_done_callback(on_task_done)

        return {
            "status": "started",
            "work_item_id": work_item_id,
            "message": "Agent processing started",
            "estimated_stages": [
                "extracting", "validating", "analyzing_risk",
                "calculating_premium", "checking_loss_history", "making_decision"
            ]
        }

    async def _process_work_item(self, work_item_id: str, work_item: Dict[str, Any]):
        """
        Process a work item through all stages.
        Updates status in Cosmos DB at each stage for real-time visibility.
        """
        try:
            # Pick a random sample submission for demo
            submission = random.choice(self.SAMPLE_SUBMISSIONS)

            # Initialize processing log
            processing_log = []

            # Stage 1: Queued
            await self._update_stage(work_item_id, ProcessingStage.QUEUED, {
                "message": "Work item queued for agent processing",
                "agent": "CREUnderwriteBot"
            }, processing_log)
            await asyncio.sleep(0.5)

            # Stage 2: Extracting
            await self._update_stage(work_item_id, ProcessingStage.EXTRACTING, {
                "message": "Extracting data from document using BDA blueprint",
                "fields_found": 0,
                "pages_processed": 0
            }, processing_log)
            await asyncio.sleep(1.5)

            extracted_data = {
                "submission_id": submission["submission_id"],
                "property_name": submission["property_name"],
                "property_type": submission["property_type"],
                "location": submission["location"],
                "tiv": submission["tiv"],
                "fields_extracted": 24,
                "extraction_confidence": 0.94,
            }
            await self._update_stage(work_item_id, ProcessingStage.EXTRACTING, {
                "message": "Document extraction complete",
                "fields_found": 24,
                "pages_processed": 10,
                "extracted_data": extracted_data
            }, processing_log)
            await asyncio.sleep(0.5)

            # Stage 3: Validating
            await self._update_stage(work_item_id, ProcessingStage.VALIDATING, {
                "message": "Validating extracted data against schema",
                "checks_passed": 0,
                "checks_total": 12
            }, processing_log)
            await asyncio.sleep(1.0)

            await self._update_stage(work_item_id, ProcessingStage.VALIDATING, {
                "message": "Validation complete - all required fields present",
                "checks_passed": 12,
                "checks_total": 12,
                "validation_result": "passed"
            }, processing_log)
            await asyncio.sleep(0.3)

            # Stage 4: Analyzing Risk
            await self._update_stage(work_item_id, ProcessingStage.ANALYZING_RISK, {
                "message": "Executing risk_score action",
                "action": "risk_score",
                "factors_analyzed": 0
            }, processing_log)
            await asyncio.sleep(1.5)

            risk_result = {
                "risk_score": submission["risk_score"],
                "risk_tier": "High" if submission["risk_score"] < 60 else "Moderate" if submission["risk_score"] < 75 else "Acceptable",
                "factors": [
                    {"factor": "Construction", "score": 85, "impact": "Positive"},
                    {"factor": "Location", "score": submission["risk_score"] - 10, "impact": "Neutral"},
                    {"factor": "Loss History", "score": submission["risk_score"] - 5, "impact": "Negative" if submission["risk_score"] < 65 else "Neutral"},
                ]
            }
            await self._update_stage(work_item_id, ProcessingStage.ANALYZING_RISK, {
                "message": f"Risk analysis complete - Score: {submission['risk_score']}/100",
                "action": "risk_score",
                "factors_analyzed": 5,
                "risk_result": risk_result
            }, processing_log)
            await asyncio.sleep(0.3)

            # Stage 5: Calculating Premium
            await self._update_stage(work_item_id, ProcessingStage.CALCULATING_PREMIUM, {
                "message": "Executing premium_calculate action",
                "action": "premium_calculate"
            }, processing_log)
            await asyncio.sleep(1.2)

            premium_result = {
                "base_premium": int(submission["premium"] * 1.2),
                "final_premium": submission["premium"],
                "rate_per_100": round(submission["premium"] / submission["tiv"] * 100, 3),
                "credits_applied": ["sprinkler_credit", "alarm_credit"],
                "debits_applied": ["loss_history"] if submission["risk_score"] < 65 else []
            }
            await self._update_stage(work_item_id, ProcessingStage.CALCULATING_PREMIUM, {
                "message": f"Premium calculated: ${submission['premium']:,}",
                "action": "premium_calculate",
                "premium_result": premium_result
            }, processing_log)
            await asyncio.sleep(0.3)

            # Stage 6: Checking Loss History
            await self._update_stage(work_item_id, ProcessingStage.CHECKING_LOSS_HISTORY, {
                "message": "Executing loss_history action",
                "action": "loss_history"
            }, processing_log)
            await asyncio.sleep(1.0)

            loss_result = {
                "total_claims": random.randint(1, 5),
                "total_paid": random.randint(100000, 2000000),
                "open_claims": 1 if submission["risk_score"] < 60 else 0,
                "loss_ratio": round(random.uniform(0.1, 0.4), 2)
            }
            await self._update_stage(work_item_id, ProcessingStage.CHECKING_LOSS_HISTORY, {
                "message": f"Loss history retrieved - {loss_result['total_claims']} claims",
                "action": "loss_history",
                "loss_result": loss_result
            }, processing_log)
            await asyncio.sleep(0.3)

            # Stage 7: Making Decision
            await self._update_stage(work_item_id, ProcessingStage.MAKING_DECISION, {
                "message": "Executing auto_decision action",
                "action": "auto_decision"
            }, processing_log)
            await asyncio.sleep(1.5)

            decision_result = {
                "decision": submission["decision"],
                "decision_text": submission["decision_text"],
                "confidence": 0.87,
                "reasons": [
                    f"Risk score: {submission['risk_score']}/100",
                    f"TIV: ${submission['tiv']:,}",
                    submission.get("approval_reason", "Standard processing")
                ],
                "conditions": [
                    "Subject to loss control inspection",
                    "Verify current occupancy rates"
                ] if submission["decision"] == "approve_with_conditions" else []
            }

            await self._update_stage(work_item_id, ProcessingStage.MAKING_DECISION, {
                "message": f"Decision: {submission['decision_text']}",
                "action": "auto_decision",
                "decision_result": decision_result
            }, processing_log)
            await asyncio.sleep(0.5)

            # Final Stage: Based on decision
            if submission["requires_approval"]:
                # Requires human approval
                final_result = {
                    "status": "requires_approval",
                    "extracted_data": extracted_data,
                    "risk_result": risk_result,
                    "premium_result": premium_result,
                    "loss_result": loss_result,
                    "decision_result": decision_result,
                    "processing_log": processing_log,
                    "requires_approval": True,
                    "approval_reason": submission["approval_reason"],
                    "recommended_approver": "Senior Underwriter" if "Senior" in submission["decision_text"] else "Underwriting Manager"
                }

                await self._update_stage(work_item_id, ProcessingStage.REQUIRES_APPROVAL, {
                    "message": f"Requires approval: {submission['approval_reason']}",
                    "recommended_approver": final_result["recommended_approver"]
                }, processing_log)

                # Update work item with final result
                await self.db.update_item(
                    {"work_item_id": work_item_id},
                    convert_floats_to_decimal({
                        "status": "needs_review",
                        "result": final_result,
                        "processing_stage": ProcessingStage.REQUIRES_APPROVAL.value,
                        "completed_at": datetime.utcnow().isoformat(),
                        "processing_log": processing_log
                    })
                )
            else:
                # Auto-approved
                final_result = {
                    "status": "approved",
                    "extracted_data": extracted_data,
                    "risk_result": risk_result,
                    "premium_result": premium_result,
                    "loss_result": loss_result,
                    "decision_result": decision_result,
                    "processing_log": processing_log,
                    "requires_approval": False,
                    "auto_approved": True,
                    "approval_timestamp": datetime.utcnow().isoformat()
                }

                await self._update_stage(work_item_id, ProcessingStage.APPROVED, {
                    "message": "Auto-approved based on risk profile"
                }, processing_log)
                await asyncio.sleep(0.3)

                await self._update_stage(work_item_id, ProcessingStage.COMPLETED, {
                    "message": "Processing complete"
                }, processing_log)

                # Update work item with final result
                await self.db.update_item(
                    {"work_item_id": work_item_id},
                    convert_floats_to_decimal({
                        "status": "completed",
                        "result": final_result,
                        "processing_stage": ProcessingStage.COMPLETED.value,
                        "completed_at": datetime.utcnow().isoformat(),
                        "processing_log": processing_log
                    })
                )

        except Exception as e:
            # Handle errors with detailed logging
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            logger.error(f"Agent processing failed for {work_item_id}",
                        error=error_msg,
                        stack_trace=stack_trace)
            print(f"ERROR in agent processing: {error_msg}")
            print(f"Stack trace: {stack_trace}")

            try:
                await self.db.update_item(
                    {"work_item_id": work_item_id},
                    {
                        "status": "failed",
                        "processing_stage": ProcessingStage.FAILED.value,
                        "last_error": error_msg,
                        "completed_at": datetime.utcnow().isoformat()
                    }
                )
            except Exception as db_error:
                logger.error(f"Failed to update failed status: {db_error}")
        finally:
            # Clean up task reference
            if work_item_id in self._processing_tasks:
                del self._processing_tasks[work_item_id]

    async def _update_stage(
        self,
        work_item_id: str,
        stage: ProcessingStage,
        details: Dict[str, Any],
        processing_log: List[Dict]
    ):
        """Update work item with current processing stage."""
        now = datetime.utcnow()

        log_entry = {
            "timestamp": now.isoformat(),
            "stage": stage.value,
            "details": convert_floats_to_decimal(details)
        }
        processing_log.append(log_entry)

        # Determine status based on stage
        status_map = {
            ProcessingStage.PENDING: "pending",
            ProcessingStage.QUEUED: "executing",
            ProcessingStage.EXTRACTING: "executing",
            ProcessingStage.VALIDATING: "executing",
            ProcessingStage.ANALYZING_RISK: "executing",
            ProcessingStage.CALCULATING_PREMIUM: "executing",
            ProcessingStage.CHECKING_LOSS_HISTORY: "executing",
            ProcessingStage.MAKING_DECISION: "executing",
            ProcessingStage.REQUIRES_APPROVAL: "needs_review",
            ProcessingStage.APPROVED: "completed",
            ProcessingStage.COMPLETED: "completed",
            ProcessingStage.FAILED: "failed",
        }

        await self.db.update_item(
            {"work_item_id": work_item_id},
            convert_floats_to_decimal({
                "status": status_map.get(stage, "executing"),
                "processing_stage": stage.value,
                "current_stage_details": details,
                "updated_at": now.isoformat(),
                "processing_log": processing_log
            })
        )

    async def approve_work_item(self, work_item_id: str, approver: str, comments: str = "") -> Dict[str, Any]:
        """Human approves a work item that requires approval."""
        work_item = await self.db.get_item({"work_item_id": work_item_id})
        if not work_item:
            return {"status": "error", "message": "Work item not found"}

        if work_item.get("status") != "needs_review":
            return {"status": "error", "message": "Work item does not require approval"}

        now = datetime.utcnow()
        result = work_item.get("result", {})
        result["approval"] = {
            "approved_by": approver,
            "approved_at": now.isoformat(),
            "comments": comments
        }
        result["status"] = "approved"

        processing_log = work_item.get("processing_log", [])
        processing_log.append({
            "timestamp": now.isoformat(),
            "stage": "approved",
            "details": {
                "message": f"Approved by {approver}",
                "comments": comments
            }
        })
        processing_log.append({
            "timestamp": now.isoformat(),
            "stage": "completed",
            "details": {"message": "Processing complete"}
        })

        await self.db.update_item(
            {"work_item_id": work_item_id},
            convert_floats_to_decimal({
                "status": "completed",
                "processing_stage": ProcessingStage.COMPLETED.value,
                "result": result,
                "processing_log": processing_log,
                "approved_by": approver,
                "approved_at": now.isoformat()
            })
        )

        return {
            "status": "success",
            "message": "Work item approved",
            "work_item_id": work_item_id,
            "approved_by": approver
        }

    async def get_processing_status(self, work_item_id: str) -> Dict[str, Any]:
        """Get current processing status with detailed stage info."""
        work_item = await self.db.get_item({"work_item_id": work_item_id})
        if not work_item:
            return {"status": "error", "message": "Work item not found"}

        return {
            "work_item_id": work_item_id,
            "status": work_item.get("status"),
            "processing_stage": work_item.get("processing_stage"),
            "current_stage_details": work_item.get("current_stage_details"),
            "processing_log": work_item.get("processing_log", []),
            "result": work_item.get("result"),
            "is_processing": work_item_id in self._processing_tasks
        }


# Global instance
agent_processor = AgentProcessorService()
