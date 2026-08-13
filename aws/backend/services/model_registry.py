"""
Multi-LLM Model Registry — single source of truth for which Bedrock models
the platform exposes, what they cost, and which task-types they're best at.

Surfaces in three places:
  1. Settings → "Agent Models" panel — per-agent dropdown options come from MODELS.
  2. AgentCore agent runtimes — read PRESETS or per-agent overrides from the
     invocation payload to switch BedrockModel at tool-call vs synthesis time.
  3. Audit Lens — looks up display_name + per-1M token cost to render
     the per-step model chip and the per-query cost estimate.

USD pricing as of 2026-04 from us-east-1 Bedrock public pricing.
Update when AWS price changes; tests assert costs are non-zero floats.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Literal, Optional


# ---------------------------------------------------------------------------
# Per-task tags — for filtering the dropdown to "what makes sense for this task"
# ---------------------------------------------------------------------------
TaskTag = Literal[
    "classification",     # intent routing, off-topic redirect
    "extraction",         # entity extraction, OCR cleanup
    "tool_selection",     # picking which @tool to call from a tool list
    "synthesis_routine",  # composing a structured response from tool outputs
    "synthesis_complex",  # multi-signal reasoning, predictive synthesis
    "summarization",      # condense a longer corpus
]


# ---------------------------------------------------------------------------
# Available models. Bedrock IDs use the inference-profile prefix (us.) where
# required — same convention as the existing AgentCore deployments.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ModelSpec:
    """A single LLM choice exposed in the Settings dropdowns."""
    id: str                          # Bedrock model id (used by BedrockModel())
    display_name: str                # human-readable, shown in dropdown
    family: str                      # vendor family for grouping
    input_cost_per_1m_usd: float     # input token cost
    output_cost_per_1m_usd: float    # output token cost
    avg_latency_ms: int              # rough cold-call latency
    suited_for: List[TaskTag]        # which task-types this model is good at
    description: str                 # one-liner for the dropdown tooltip
    requires_inference_profile: bool = True  # most Bedrock models need 'us.' prefix

    def to_dict(self) -> Dict[str, object]:
        d = asdict(self)
        # Compute a typical-query cost estimate (3K input + 500 output tokens)
        d["estimated_query_cost_usd"] = round(
            (3000 / 1_000_000) * self.input_cost_per_1m_usd
            + (500 / 1_000_000) * self.output_cost_per_1m_usd,
            5,
        )
        return d


# Hand-curated set of 9 models that span the cost/quality frontier.
# The platform supports more (any Bedrock model id works), but the dropdown
# is opinionated — too many choices is a UX failure mode.
MODELS: List[ModelSpec] = [
    ModelSpec(
        id="amazon.nova-micro-v1:0",
        display_name="Nova Micro",
        family="amazon",
        input_cost_per_1m_usd=0.035,
        output_cost_per_1m_usd=0.14,
        avg_latency_ms=600,
        suited_for=["classification", "extraction"],
        description="Fastest + cheapest. Great for intent routing & simple extraction.",
        requires_inference_profile=False,
    ),
    ModelSpec(
        id="amazon.nova-lite-v1:0",
        display_name="Nova Lite",
        family="amazon",
        input_cost_per_1m_usd=0.06,
        output_cost_per_1m_usd=0.24,
        avg_latency_ms=900,
        suited_for=["extraction", "tool_selection", "summarization"],
        description="Cheap multimodal. OCR cleanup + light tool selection.",
        requires_inference_profile=False,
    ),
    ModelSpec(
        id="meta.llama3-3-70b-instruct-v1:0",
        display_name="Llama 3.3 70B",
        family="meta",
        input_cost_per_1m_usd=0.30,
        output_cost_per_1m_usd=0.40,
        avg_latency_ms=1400,
        suited_for=["tool_selection", "summarization"],
        description="Strong open-weight model. Solid for tool selection.",
        requires_inference_profile=False,
    ),
    ModelSpec(
        id="us.deepseek.r1-v1:0",
        display_name="DeepSeek R1",
        family="deepseek",
        input_cost_per_1m_usd=0.55,
        output_cost_per_1m_usd=2.19,
        avg_latency_ms=2200,
        suited_for=["synthesis_routine", "synthesis_complex"],
        description="Reasoning-heavy at fraction of Opus cost. Math & multi-step.",
    ),
    ModelSpec(
        id="us.anthropic.claude-haiku-3-5-v1",
        display_name="Haiku 3.5",
        family="anthropic",
        input_cost_per_1m_usd=0.80,
        output_cost_per_1m_usd=4.00,
        avg_latency_ms=1100,
        suited_for=["tool_selection", "extraction", "summarization"],
        description="Workhorse for tool calls. 4x cheaper than Sonnet.",
    ),
    ModelSpec(
        id="amazon.nova-pro-v1:0",
        display_name="Nova Pro",
        family="amazon",
        input_cost_per_1m_usd=0.80,
        output_cost_per_1m_usd=3.20,
        avg_latency_ms=1600,
        suited_for=["synthesis_routine", "summarization"],
        description="Structured composition. Stronger reasoning than Lite.",
        requires_inference_profile=False,
    ),
    ModelSpec(
        id="mistral.mistral-large-2407-v1:0",
        display_name="Mistral Large 2",
        family="mistral",
        input_cost_per_1m_usd=2.00,
        output_cost_per_1m_usd=6.00,
        avg_latency_ms=1700,
        suited_for=["synthesis_routine", "tool_selection"],
        description="Alt synthesis option. EU-hosted-friendly.",
        requires_inference_profile=False,
    ),
    ModelSpec(
        id="us.anthropic.claude-sonnet-4-5-v1",
        display_name="Sonnet 4.5",
        family="anthropic",
        input_cost_per_1m_usd=3.00,
        output_cost_per_1m_usd=15.00,
        avg_latency_ms=1900,
        suited_for=["synthesis_routine", "synthesis_complex", "summarization"],
        description="Best price/performance for synthesis. Recommended default.",
    ),
    ModelSpec(
        id="us.anthropic.claude-opus-4-6-v1",
        display_name="Opus 4.6",
        family="anthropic",
        input_cost_per_1m_usd=15.00,
        output_cost_per_1m_usd=75.00,
        avg_latency_ms=3500,
        suited_for=["synthesis_complex"],
        description="Strongest reasoning. Reserve for complex multi-signal tasks.",
    ),
    # ─── OpenAI (via Azure OpenAI proxy or direct API key) ───
    # Surfaced in the Settings dropdown for customers who want to evaluate
    # GPT-class models alongside Bedrock. Routing layer needs an API-key
    # backend (see backend/services/openai_client.py — out of scope today;
    # these entries are catalog-only for the Settings picker UI).
    ModelSpec(
        id="openai.gpt-4o-mini",
        display_name="GPT-4o mini",
        family="openai",
        input_cost_per_1m_usd=0.15,
        output_cost_per_1m_usd=0.60,
        avg_latency_ms=900,
        suited_for=["tool_selection", "extraction", "summarization"],
        description="OpenAI's cheap fast model. Closest to Haiku on price/speed.",
        requires_inference_profile=False,
    ),
    ModelSpec(
        id="openai.gpt-4o",
        display_name="GPT-4o",
        family="openai",
        input_cost_per_1m_usd=2.50,
        output_cost_per_1m_usd=10.00,
        avg_latency_ms=1700,
        suited_for=["synthesis_routine", "synthesis_complex", "summarization"],
        description="OpenAI flagship multimodal. Comparable to Sonnet for synthesis.",
        requires_inference_profile=False,
    ),
    ModelSpec(
        id="openai.gpt-4-turbo",
        display_name="GPT-4 Turbo",
        family="openai",
        input_cost_per_1m_usd=10.00,
        output_cost_per_1m_usd=30.00,
        avg_latency_ms=2400,
        suited_for=["synthesis_complex"],
        description="OpenAI's reasoning workhorse. Heavier than 4o.",
        requires_inference_profile=False,
    ),
    ModelSpec(
        id="openai.o1-mini",
        display_name="o1-mini (reasoning)",
        family="openai",
        input_cost_per_1m_usd=3.00,
        output_cost_per_1m_usd=12.00,
        avg_latency_ms=4500,
        suited_for=["synthesis_complex"],
        description="OpenAI o1-class chain-of-thought. Slow but strong on math/code.",
        requires_inference_profile=False,
    ),
]


def get_model(model_id: str) -> Optional[ModelSpec]:
    """Look up a ModelSpec by Bedrock id. Returns None if not in registry."""
    return next((m for m in MODELS if m.id == model_id), None)


def list_models() -> List[Dict[str, object]]:
    """Serializable list for the GET /llm/models endpoint."""
    return [m.to_dict() for m in MODELS]


# ---------------------------------------------------------------------------
# Per-agent task slots — defines what dropdowns the Settings UI shows for
# each STP agent. Each slot has a default model id (used when the user
# hasn't customized).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AgentSlot:
    """A single dropdown on the Settings panel — e.g. PolicyAgent's 'tool calls'."""
    key: str                # canonical slot key, used in payload routing
    label: str              # what the dropdown says
    task_tag: TaskTag       # filters dropdown options to suitable models
    default_id: str         # model id picked by Quality-First strategy


@dataclass(frozen=True)
class AgentSpec:
    """An agent (or router) and its configurable slots."""
    id: str                       # canonical agent id (matches AGENT_ARNS keys)
    display_name: str             # what shows on the card
    use_case: str                 # 'router', 'UC-1', 'UC-2', etc.
    description: str              # one-liner for the card subtitle
    why: str                      # rationale shown under the dropdowns
    slots: List[AgentSlot]


AGENTS: List[AgentSpec] = [
    AgentSpec(
        id="chatstp",
        display_name="ChatSTP Router",
        use_case="router",
        description="Classifies the user query and delegates to specialists",
        why="Routing is pattern matching, not reasoning — Haiku is plenty.",
        slots=[
            AgentSlot(
                key="routing", label="Routing logic",
                task_tag="classification",
                default_id="us.anthropic.claude-haiku-3-5-v1",
            ),
        ],
    ),
    AgentSpec(
        id="policy-agent",
        display_name="PolicyAgent",
        use_case="UC-1",
        description="Verbatim citation of HR policies, procedures, Tech Specs",
        why="BM25 search + verbatim citation. No novel reasoning needed.",
        slots=[
            AgentSlot(
                key="tool_selection", label="Tool selection",
                task_tag="tool_selection",
                default_id="amazon.nova-lite-v1:0",
            ),
            AgentSlot(
                key="synthesis", label="Final answer",
                task_tag="synthesis_routine",
                default_id="us.anthropic.claude-sonnet-4-5-v1",
            ),
        ],
    ),
    AgentSpec(
        id="maintenance-agent",
        display_name="MaintenanceAgent",
        use_case="UC-2",
        description="Equipment PM history with engineer attribution",
        why="SQL-style joins, deterministic. Haiku handles this fine.",
        slots=[
            AgentSlot(
                key="tool_selection", label="Tool selection",
                task_tag="tool_selection",
                default_id="us.anthropic.claude-haiku-3-5-v1",
            ),
            AgentSlot(
                key="synthesis", label="Final answer",
                task_tag="synthesis_routine",
                default_id="us.anthropic.claude-haiku-3-5-v1",
            ),
        ],
    ),
    AgentSpec(
        id="diagnostics-agent",
        display_name="DiagnosticsAgent",
        use_case="UC-3",
        description="Failure-mode aggregation with cited WO evidence",
        why="Pattern aggregation across WO corpus — mid-tier reasoning.",
        slots=[
            AgentSlot(
                key="tool_selection", label="Tool selection",
                task_tag="tool_selection",
                default_id="us.anthropic.claude-haiku-3-5-v1",
            ),
            AgentSlot(
                key="synthesis", label="Final answer",
                task_tag="synthesis_routine",
                default_id="us.anthropic.claude-sonnet-4-5-v1",
            ),
        ],
    ),
    AgentSpec(
        id="reliability-agent",
        display_name="ReliabilityAgent",
        use_case="UC-4",
        description="Predictive maintenance with multi-signal reasoning",
        why="THIS one needs Opus — synthesizing anomaly + history + recommendation.",
        slots=[
            AgentSlot(
                key="tool_selection", label="Tool selection",
                task_tag="tool_selection",
                default_id="us.anthropic.claude-haiku-3-5-v1",
            ),
            AgentSlot(
                key="synthesis", label="Final answer",
                task_tag="synthesis_complex",
                default_id="us.anthropic.claude-opus-4-6-v1",
            ),
        ],
    ),
]


def get_agent(agent_id: str) -> Optional[AgentSpec]:
    """Look up an AgentSpec by id."""
    norm = agent_id.replace("_", "-").lower()
    return next((a for a in AGENTS if a.id == norm), None)


def list_agents() -> List[Dict[str, object]]:
    """Serializable list for the GET /llm/agents endpoint."""
    return [
        {
            "id": a.id,
            "display_name": a.display_name,
            "use_case": a.use_case,
            "description": a.description,
            "why": a.why,
            "slots": [
                {**asdict(s), "default_model": get_model(s.default_id).to_dict() if get_model(s.default_id) else None}
                for s in a.slots
            ],
        }
        for a in AGENTS
    ]


# ---------------------------------------------------------------------------
# Strategy presets — one-click "set all 10 dropdowns at once"
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class StrategyPreset:
    """A named one-click preset that fills in every agent slot."""
    id: str
    display_name: str
    icon: str               # emoji shown on the preset button
    description: str
    overrides: Dict[str, Dict[str, str]]   # {agent_id: {slot_key: model_id}}


PRESETS: List[StrategyPreset] = [
    StrategyPreset(
        id="cost_optimized",
        display_name="Cost-Optimized",
        icon="⚡",
        description="Nova/Haiku where possible. Sonnet only for ReliabilityAgent synth. ~88% savings.",
        overrides={
            "chatstp":             {"routing": "amazon.nova-micro-v1:0"},
            "policy-agent":        {"tool_selection": "amazon.nova-lite-v1:0", "synthesis": "us.anthropic.claude-haiku-3-5-v1"},
            "maintenance-agent":   {"tool_selection": "amazon.nova-lite-v1:0", "synthesis": "us.anthropic.claude-haiku-3-5-v1"},
            "diagnostics-agent":   {"tool_selection": "amazon.nova-lite-v1:0", "synthesis": "us.anthropic.claude-haiku-3-5-v1"},
            "reliability-agent":   {"tool_selection": "amazon.nova-lite-v1:0", "synthesis": "us.anthropic.claude-sonnet-4-5-v1"},
        },
    ),
    StrategyPreset(
        id="balanced",
        display_name="Balanced",
        icon="⚖️",
        description="Sonnet workhorse, Opus only for ReliabilityAgent synth. Recommended default. ~79% savings vs Quality-First.",
        overrides={
            "chatstp":             {"routing": "us.anthropic.claude-haiku-3-5-v1"},
            "policy-agent":        {"tool_selection": "amazon.nova-lite-v1:0", "synthesis": "us.anthropic.claude-sonnet-4-5-v1"},
            "maintenance-agent":   {"tool_selection": "us.anthropic.claude-haiku-3-5-v1", "synthesis": "us.anthropic.claude-haiku-3-5-v1"},
            "diagnostics-agent":   {"tool_selection": "us.anthropic.claude-haiku-3-5-v1", "synthesis": "us.anthropic.claude-sonnet-4-5-v1"},
            "reliability-agent":   {"tool_selection": "us.anthropic.claude-haiku-3-5-v1", "synthesis": "us.anthropic.claude-opus-4-6-v1"},
        },
    ),
    StrategyPreset(
        id="quality_first",
        display_name="Quality-First",
        icon="💎",
        description="Opus 4.6 everywhere. Maximum reasoning, maximum cost. Use for compliance/QA mode.",
        overrides={
            "chatstp":             {"routing": "us.anthropic.claude-opus-4-6-v1"},
            "policy-agent":        {"tool_selection": "us.anthropic.claude-opus-4-6-v1", "synthesis": "us.anthropic.claude-opus-4-6-v1"},
            "maintenance-agent":   {"tool_selection": "us.anthropic.claude-opus-4-6-v1", "synthesis": "us.anthropic.claude-opus-4-6-v1"},
            "diagnostics-agent":   {"tool_selection": "us.anthropic.claude-opus-4-6-v1", "synthesis": "us.anthropic.claude-opus-4-6-v1"},
            "reliability-agent":   {"tool_selection": "us.anthropic.claude-opus-4-6-v1", "synthesis": "us.anthropic.claude-opus-4-6-v1"},
        },
    ),
]


def get_preset(preset_id: str) -> Optional[StrategyPreset]:
    return next((p for p in PRESETS if p.id == preset_id), None)


def list_presets() -> List[Dict[str, object]]:
    """Serializable list for the GET /llm/presets endpoint, including per-preset cost estimate."""
    out: List[Dict[str, object]] = []
    for p in PRESETS:
        # Cost estimate = sum of per-slot estimated query cost across all agents
        cost = 0.0
        for agent in AGENTS:
            slot_overrides = p.overrides.get(agent.id, {})
            for slot in agent.slots:
                model_id = slot_overrides.get(slot.key, slot.default_id)
                m = get_model(model_id)
                if m:
                    cost += (m.input_cost_per_1m_usd * 3000 + m.output_cost_per_1m_usd * 500) / 1_000_000
        out.append({
            "id": p.id,
            "display_name": p.display_name,
            "icon": p.icon,
            "description": p.description,
            "overrides": p.overrides,
            "estimated_query_cost_usd": round(cost, 5),
        })
    return out


# ---------------------------------------------------------------------------
# Resolution helper — given a possibly-empty user override map, fill in
# defaults so callers always get a complete model assignment per slot.
# ---------------------------------------------------------------------------
def resolve_model_for_agent_slot(
    agent_id: str,
    slot_key: str,
    user_overrides: Optional[Dict[str, Dict[str, str]]] = None,
) -> ModelSpec:
    """Resolve which ModelSpec an agent should use for a given slot.

    Resolution order:
      1. user_overrides[agent_id][slot_key]    — explicit user pick
      2. AGENTS[agent_id].slots[slot].default_id — registry default
      3. fall through to Sonnet 4.5 if nothing matches (defensive)
    """
    overrides = user_overrides or {}
    agent = get_agent(agent_id)
    if not agent:
        return get_model("us.anthropic.claude-sonnet-4-5-v1")  # type: ignore[return-value]

    slot = next((s for s in agent.slots if s.key == slot_key), None)
    if not slot:
        return get_model("us.anthropic.claude-sonnet-4-5-v1")  # type: ignore[return-value]

    chosen_id = overrides.get(agent.id, {}).get(slot.key, slot.default_id)
    spec = get_model(chosen_id) or get_model(slot.default_id)
    return spec or get_model("us.anthropic.claude-sonnet-4-5-v1")  # type: ignore[return-value]


def estimate_query_cost(
    overrides: Optional[Dict[str, Dict[str, str]]] = None,
    intent: str = "policy_lookup",
) -> Dict[str, object]:
    """Estimate per-query cost for a hypothetical query of the given intent.

    Sums the routing cost (always) + the chosen specialist's tool + synth costs.
    Returns a breakdown the UI can show in the cost estimator footer.
    """
    overrides = overrides or {}
    breakdown: List[Dict[str, object]] = []

    # Router always runs
    router_model = resolve_model_for_agent_slot("chatstp", "routing", overrides)
    router_cost = (router_model.input_cost_per_1m_usd * 800 + router_model.output_cost_per_1m_usd * 100) / 1_000_000
    breakdown.append({
        "step": "router",
        "agent": "chatstp", "slot": "routing",
        "model_id": router_model.id, "model_display": router_model.display_name,
        "tokens_in": 800, "tokens_out": 100,
        "cost_usd": round(router_cost, 5),
    })

    # Map intent to specialist
    specialist = {
        "policy_lookup": "policy-agent",
        "maintenance_history": "maintenance-agent",
        "issue_analysis": "diagnostics-agent",
        "predictive_maintenance": "reliability-agent",
    }.get(intent, "policy-agent")

    tool_model = resolve_model_for_agent_slot(specialist, "tool_selection", overrides)
    tool_cost = (tool_model.input_cost_per_1m_usd * 1500 + tool_model.output_cost_per_1m_usd * 200) / 1_000_000
    breakdown.append({
        "step": "tool_selection",
        "agent": specialist, "slot": "tool_selection",
        "model_id": tool_model.id, "model_display": tool_model.display_name,
        "tokens_in": 1500, "tokens_out": 200,
        "cost_usd": round(tool_cost, 5),
    })

    synth_model = resolve_model_for_agent_slot(specialist, "synthesis", overrides)
    synth_cost = (synth_model.input_cost_per_1m_usd * 2500 + synth_model.output_cost_per_1m_usd * 400) / 1_000_000
    breakdown.append({
        "step": "synthesis",
        "agent": specialist, "slot": "synthesis",
        "model_id": synth_model.id, "model_display": synth_model.display_name,
        "tokens_in": 2500, "tokens_out": 400,
        "cost_usd": round(synth_cost, 5),
    })

    return {
        "intent": intent,
        "breakdown": breakdown,
        "total_cost_usd": round(router_cost + tool_cost + synth_cost, 5),
    }
