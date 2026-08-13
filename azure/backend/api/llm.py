"""
Multi-LLM API — exposes the model registry to the Settings page.

Endpoints:
  GET  /api/v1/llm/models                  — List of available Azure OpenAI models
  GET  /api/v1/llm/agents                  — Per-agent slot specs (router + 4)
  GET  /api/v1/llm/presets                 — 3 named strategy presets
  POST /api/v1/llm/estimate                — Per-query cost estimate given overrides

The frontend's Settings → AgentModelsPanel calls /agents and /presets on mount,
then /estimate on every dropdown change to refresh the cost footer.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.model_registry import (
    list_models, list_agents, list_presets, estimate_query_cost,
)

router = APIRouter()


@router.get("/models")
async def get_models() -> Dict[str, Any]:
    """List the 9 Azure OpenAI models exposed in the dropdowns, with pricing.

    Returns:
        { "models": [...], "count": 9 }
    """
    items = list_models()
    return {"models": items, "count": len(items)}


@router.get("/agents")
async def get_agents() -> Dict[str, Any]:
    """List the 5 STP agents and their configurable model slots.

    Each agent has 1+ slots (router has 1, all specialists have 2:
    tool_selection + synthesis). Each slot includes the registry default.

    Returns:
        { "agents": [...], "count": 5 }
    """
    items = list_agents()
    return {"agents": items, "count": len(items)}


@router.get("/presets")
async def get_presets() -> Dict[str, Any]:
    """List the 3 strategy presets with per-preset cost estimates.

    Returns:
        { "presets": [...], "count": 3 }
    """
    items = list_presets()
    return {"presets": items, "count": len(items)}


class EstimateRequest(BaseModel):
    """Frontend sends the user's current overrides + intent."""
    overrides: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Same shape as LLMConfig: {agent_id: {slot_key: model_id}}",
    )
    intent: str = Field(
        default="policy_lookup",
        description="Which UC the cost estimate should target",
    )


@router.post("/estimate")
async def estimate(req: EstimateRequest) -> Dict[str, Any]:
    """Per-query cost estimate for a given override config + intent.

    Used by the Settings page to refresh the "Estimated cost per query" footer
    each time the user changes a dropdown. Also used by the Dashboard tile
    to show projected vs baseline cost.

    Returns:
        {
          "intent": "...",
          "breakdown": [{step, agent, slot, model_id, model_display, tokens_in, tokens_out, cost_usd}, ...],
          "total_cost_usd": float
        }
    """
    return estimate_query_cost(req.overrides, req.intent)
