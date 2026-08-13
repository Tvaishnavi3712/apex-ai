"""
Small Factory Engine
Modular, chainable automation units inspired by Uniphore's architecture.
Each factory is a self-contained processing unit that can be composed into workflows.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import structlog
import yaml
from pathlib import Path

logger = structlog.get_logger()


class FactoryStatus(str, Enum):
    """Status of a factory execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class FactoryDefinition:
    """Definition of a Small Factory"""
    id: str
    action: str
    depends_on: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    parallel: bool = False  # Can run in parallel with siblings
    timeout_seconds: int = 60
    retry_count: int = 0
    context_keys: List[str] = field(default_factory=list)  # Context sections this factory needs
    ai_enhanced: bool = False  # Whether this factory uses AI enhancement


@dataclass
class FactoryResult:
    """Result of a factory execution"""
    factory_id: str
    status: FactoryStatus
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class ChainDefinition:
    """Definition of a factory chain"""
    name: str
    description: str
    factories: List[FactoryDefinition]
    outputs: List[str] = field(default_factory=list)


class SmallFactoryEngine:
    """
    Engine for executing Small Factory chains.

    Features:
    - Dependency resolution (DAG execution)
    - Parallel execution of independent factories
    - State passing between factories
    - Error handling and retries
    - Real-time progress callbacks
    """

    def __init__(self):
        self._handlers: Dict[str, Callable] = {}
        self._chains: Dict[str, ChainDefinition] = {}
        self._load_chain_definitions()

    def register_handler(self, action_name: str, handler: Callable):
        """Register a handler function for an action type."""
        self._handlers[action_name] = handler
        logger.info("Registered factory handler", action=action_name)

    def _load_chain_definitions(self):
        """Load chain definitions from YAML config."""
        config_path = Path(__file__).parent.parent / "config" / "factory_chains.yaml"
        if config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f)
                for chain_id, chain_data in data.get('chains', {}).items():
                    factories = []
                    for f in chain_data.get('factories', []):
                        # Handle context_keys which may be in factory definition
                        factory_def = FactoryDefinition(
                            id=f.get('id'),
                            action=f.get('action'),
                            depends_on=f.get('depends_on', []),
                            config=f.get('config', {}),
                            parallel=f.get('parallel', False),
                            timeout_seconds=f.get('timeout_seconds', 60),
                            retry_count=f.get('retry_count', 0),
                            context_keys=f.get('context_keys', []),
                            ai_enhanced=f.get('ai_enhanced', f.get('aiEnhanced', False))
                        )
                        factories.append(factory_def)

                    self._chains[chain_id] = ChainDefinition(
                        name=chain_data.get('name', chain_id),
                        description=chain_data.get('description', ''),
                        factories=factories,
                        outputs=chain_data.get('outputs', [])
                    )
            logger.info("Loaded factory chains", count=len(self._chains))

    def load_chain_from_playbook(self, playbook_data: Dict[str, Any]) -> Optional[str]:
        """
        Load a factory chain from a playbook definition.

        Args:
            playbook_data: Parsed playbook YAML data

        Returns:
            Chain ID if loaded successfully
        """
        factory_chain = playbook_data.get('factory_chain')
        if not factory_chain:
            return None

        chain_id = factory_chain.get('chainId', factory_chain.get('chain_id'))
        if not chain_id:
            return None

        factories = []
        for f in factory_chain.get('factories', []):
            factory_def = FactoryDefinition(
                id=f.get('id'),
                action=f.get('action', f.get('id')),  # Default action to id if not specified
                depends_on=f.get('depends_on', []),
                config=f.get('config', {}),
                parallel=f.get('parallel', False),
                timeout_seconds=f.get('timeout_seconds', 60),
                retry_count=f.get('retry_count', 0),
                context_keys=f.get('context_keys', []),
                ai_enhanced=f.get('ai_enhanced', f.get('aiEnhanced', False))
            )
            factories.append(factory_def)

        self._chains[chain_id] = ChainDefinition(
            name=factory_chain.get('name', chain_id),
            description=factory_chain.get('description', ''),
            factories=factories,
            outputs=factory_chain.get('outputs', [])
        )

        logger.info("Loaded chain from playbook", chain_id=chain_id, factory_count=len(factories))
        return chain_id

    def get_chain(self, chain_id: str) -> Optional[ChainDefinition]:
        """Get a chain definition by ID."""
        return self._chains.get(chain_id)

    def list_chains(self) -> List[Dict[str, Any]]:
        """List all available chains."""
        return [
            {
                "id": chain_id,
                "name": chain.name,
                "description": chain.description,
                "factory_count": len(chain.factories)
            }
            for chain_id, chain in self._chains.items()
        ]

    async def execute_chain(
        self,
        chain_id: str,
        initial_input: Dict[str, Any],
        progress_callback: Optional[Callable[[str, FactoryResult], None]] = None,
        playbook_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a factory chain with context-driven rules.

        Args:
            chain_id: ID of the chain to execute
            initial_input: Initial input data for the chain
            progress_callback: Optional callback for progress updates
            playbook_context: Context from playbook containing business rules

        Returns:
            Final results from all factories
        """
        chain = self.get_chain(chain_id)
        if not chain:
            raise ValueError(f"Chain {chain_id} not found")

        execution_id = str(uuid.uuid4())
        context_driven = bool(playbook_context)
        logger.info(
            "Starting chain execution",
            chain_id=chain_id,
            execution_id=execution_id,
            context_driven=context_driven
        )

        # Build execution plan (topological sort)
        execution_order = self._build_execution_order(chain.factories)

        # Track state
        state: Dict[str, Any] = {"input": initial_input}
        results: Dict[str, FactoryResult] = {}
        completed: Set[str] = set()

        # Execute in dependency order
        for layer in execution_order:
            # Execute factories in this layer in parallel
            tasks = []
            for factory in layer:
                # Check if dependencies are met
                deps_met = all(dep in completed for dep in factory.depends_on)
                if not deps_met:
                    logger.error(
                        "Dependencies not met",
                        factory=factory.id,
                        missing=[d for d in factory.depends_on if d not in completed]
                    )
                    continue

                # Build input from state and dependency outputs
                factory_input = self._build_factory_input(factory, state, results)

                # Build factory-specific context from playbook context
                factory_context = self._build_factory_context(factory, playbook_context)

                # Create execution task with context
                task = self._execute_factory(factory, factory_input, progress_callback, factory_context)
                tasks.append((factory.id, task))

            # Wait for all tasks in this layer
            for factory_id, task in tasks:
                try:
                    result = await task
                    results[factory_id] = result
                    completed.add(factory_id)

                    # Update state with outputs
                    if result.status == FactoryStatus.COMPLETED:
                        state[factory_id] = result.output

                except Exception as e:
                    logger.error("Factory execution failed", factory_id=factory_id, error=str(e))
                    results[factory_id] = FactoryResult(
                        factory_id=factory_id,
                        status=FactoryStatus.FAILED,
                        error=str(e)
                    )

        # Build final output
        final_output = {
            "execution_id": execution_id,
            "chain_id": chain_id,
            "status": "completed" if all(r.status == FactoryStatus.COMPLETED for r in results.values()) else "partial",
            "context_driven": context_driven,
            "results": {
                fid: {
                    "status": r.status.value,
                    "output": r.output,
                    "duration_ms": r.duration_ms,
                    "error": r.error
                }
                for fid, r in results.items()
            },
            "state": state,
            "completed_at": datetime.utcnow().isoformat()
        }

        # Extract specified outputs
        final_output["outputs"] = {
            key: state.get(key)
            for key in chain.outputs
            if key in state
        }

        return final_output

    def _build_factory_context(
        self,
        factory: FactoryDefinition,
        playbook_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build context for a factory based on its context_keys.

        If factory specifies context_keys, only those sections are included.
        Otherwise, the entire playbook context is passed.
        """
        if not playbook_context:
            return {}

        # If factory specifies context_keys, filter to only those
        if factory.context_keys:
            return {
                key: playbook_context[key]
                for key in factory.context_keys
                if key in playbook_context
            }

        # Otherwise pass full context
        return playbook_context

    def _build_execution_order(self, factories: List[FactoryDefinition]) -> List[List[FactoryDefinition]]:
        """
        Build execution order using topological sort.
        Returns layers of factories that can be executed in parallel.
        """
        # Build dependency graph
        factory_map = {f.id: f for f in factories}
        in_degree = {f.id: len(f.depends_on) for f in factories}
        dependents = {f.id: [] for f in factories}

        for f in factories:
            for dep in f.depends_on:
                if dep in dependents:
                    dependents[dep].append(f.id)

        # Kahn's algorithm for topological sort
        layers = []
        ready = [fid for fid, degree in in_degree.items() if degree == 0]

        while ready:
            # Current layer
            layer = [factory_map[fid] for fid in ready]
            layers.append(layer)

            # Find next layer
            next_ready = []
            for fid in ready:
                for dependent in dependents[fid]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_ready.append(dependent)

            ready = next_ready

        return layers

    def _build_factory_input(
        self,
        factory: FactoryDefinition,
        state: Dict[str, Any],
        results: Dict[str, FactoryResult]
    ) -> Dict[str, Any]:
        """Build input for a factory from state and dependency outputs."""
        factory_input = {
            "config": factory.config,
            "initial_input": state.get("input", {}),
        }

        # Add outputs from dependencies
        for dep in factory.depends_on:
            if dep in results and results[dep].status == FactoryStatus.COMPLETED:
                factory_input[dep] = results[dep].output

        # Add full state access
        factory_input["state"] = state

        return factory_input

    async def _execute_factory(
        self,
        factory: FactoryDefinition,
        input_data: Dict[str, Any],
        progress_callback: Optional[Callable],
        context: Optional[Dict[str, Any]] = None
    ) -> FactoryResult:
        """Execute a single factory with context-driven rules."""
        started_at = datetime.utcnow()

        # Notify progress
        if progress_callback:
            progress_callback(factory.id, FactoryResult(
                factory_id=factory.id,
                status=FactoryStatus.RUNNING,
                started_at=started_at.isoformat()
            ))

        try:
            # Get handler
            handler = self._handlers.get(factory.action)
            if not handler:
                raise ValueError(f"No handler registered for action: {factory.action}")

            # Execute with timeout, passing context to handler
            try:
                if asyncio.iscoroutinefunction(handler):
                    # Try to call with context parameter (new signature)
                    import inspect
                    sig = inspect.signature(handler)
                    if 'context' in sig.parameters:
                        output = await asyncio.wait_for(
                            handler(input_data, context=context),
                            timeout=factory.timeout_seconds
                        )
                    else:
                        # Legacy handler without context support
                        output = await asyncio.wait_for(
                            handler(input_data),
                            timeout=factory.timeout_seconds
                        )
                else:
                    # Sync handler
                    import inspect
                    sig = inspect.signature(handler)
                    if 'context' in sig.parameters:
                        output = await asyncio.wait_for(
                            asyncio.to_thread(handler, input_data, context=context),
                            timeout=factory.timeout_seconds
                        )
                    else:
                        output = await asyncio.wait_for(
                            asyncio.to_thread(handler, input_data),
                            timeout=factory.timeout_seconds
                        )
            except asyncio.TimeoutError:
                raise TimeoutError(f"Factory {factory.id} timed out after {factory.timeout_seconds}s")

            completed_at = datetime.utcnow()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)

            result = FactoryResult(
                factory_id=factory.id,
                status=FactoryStatus.COMPLETED,
                output=output or {},
                duration_ms=duration_ms,
                started_at=started_at.isoformat(),
                completed_at=completed_at.isoformat()
            )

        except Exception as e:
            completed_at = datetime.utcnow()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)

            result = FactoryResult(
                factory_id=factory.id,
                status=FactoryStatus.FAILED,
                error=str(e),
                duration_ms=duration_ms,
                started_at=started_at.isoformat(),
                completed_at=completed_at.isoformat()
            )

            logger.error(
                "Factory execution failed",
                factory_id=factory.id,
                action=factory.action,
                error=str(e),
                context_driven=bool(context)
            )

        # Notify progress
        if progress_callback:
            progress_callback(factory.id, result)

        return result

    async def execute_single(
        self,
        action: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> FactoryResult:
        """Execute a single factory without chaining, with optional context."""
        factory = FactoryDefinition(
            id=f"single-{uuid.uuid4().hex[:8]}",
            action=action,
            config=config or {}
        )

        return await self._execute_factory(
            factory,
            {"config": config or {}, "initial_input": input_data, "state": {}},
            None,
            context=context
        )


# Global engine instance
_engine: Optional[SmallFactoryEngine] = None


def get_factory_engine() -> SmallFactoryEngine:
    """Get the global factory engine instance."""
    global _engine
    if _engine is None:
        _engine = SmallFactoryEngine()
    return _engine


def register_factory(action_name: str):
    """Decorator to register a function as a factory handler."""
    def decorator(func: Callable):
        get_factory_engine().register_handler(action_name, func)
        return func
    return decorator
