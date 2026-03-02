"""
Auto-Pilot Pipeline for Antigravity Workspace
Autonomous multi-stage pipeline that chains agents together to complete goals end-to-end.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable

logger = logging.getLogger(__name__)


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class PipelineStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineStage:
    """A single stage in the auto-pilot pipeline."""
    name: str
    agent_name: str
    description: str
    status: StageStatus = StageStatus.PENDING
    result: Optional[str] = None
    artifact_id: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "agent_name": self.agent_name,
            "description": self.description,
            "status": self.status.value,
            "result_preview": self.result[:200] if self.result else None,
            "artifact_id": self.artifact_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": (
                (self.completed_at - self.started_at) * 1000
                if self.started_at and self.completed_at
                else None
            ),
            "error": self.error,
        }


@dataclass
class Pipeline:
    """A complete auto-pilot pipeline execution."""
    id: str
    goal: str
    status: PipelineStatus = PipelineStatus.CREATED
    stages: List[PipelineStage] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    current_stage_index: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "status": self.status.value,
            "stages": [s.to_dict() for s in self.stages],
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "current_stage_index": self.current_stage_index,
            "progress_pct": self._progress_pct(),
            "error": self.error,
        }

    def _progress_pct(self) -> int:
        if not self.stages:
            return 0
        completed = sum(
            1 for s in self.stages if s.status in (StageStatus.COMPLETED, StageStatus.SKIPPED)
        )
        return int(completed / len(self.stages) * 100)


# Default pipeline stages: (name, agent, description)
DEFAULT_STAGES = [
    ("plan", "architect", "Analyze the goal and create an implementation plan"),
    ("implement", "full-stack-developer", "Write the code based on the plan"),
    ("review", "code-reviewer", "Review the code for quality, security, and best practices"),
    ("test", "testing-stability-expert", "Write and run tests to validate the implementation"),
    ("optimize", "performance-optimizer", "Optimize performance if needed"),
]


class AutoPilotPipeline:
    """
    Manages autonomous multi-stage pipelines that chain agents together.
    
    Each pipeline flows through defined stages (plan → implement → review → test → optimize),
    with each stage delegated to the appropriate specialist agent.
    """

    def __init__(
        self,
        orchestrator=None,
        agent_manager=None,
        broadcast_fn: Optional[Callable] = None,
    ):
        """
        Args:
            orchestrator: Orchestrator instance for processing requests
            agent_manager: AgentManager instance for agent lookup
            broadcast_fn: Optional async callable to broadcast progress updates
        """
        self.orchestrator = orchestrator
        self.agent_manager = agent_manager
        self.broadcast_fn = broadcast_fn
        self._pipelines: Dict[str, Pipeline] = {}
        self._tasks: Dict[str, asyncio.Task] = {}

    def start(self, goal: str, stages: Optional[List[tuple]] = None) -> str:
        """
        Start a new auto-pilot pipeline.
        
        Args:
            goal: The user's goal description
            stages: Optional custom stages list of (name, agent_name, description)
            
        Returns:
            Pipeline ID
        """
        pipeline_id = str(uuid.uuid4())[:8]
        stage_defs = stages or DEFAULT_STAGES

        pipeline = Pipeline(
            id=pipeline_id,
            goal=goal,
            stages=[
                PipelineStage(name=name, agent_name=agent, description=desc)
                for name, agent, desc in stage_defs
            ],
        )

        self._pipelines[pipeline_id] = pipeline

        # Launch async execution
        task = asyncio.ensure_future(self._run_pipeline(pipeline_id))
        self._tasks[pipeline_id] = task

        logger.info(f"Auto-Pilot pipeline {pipeline_id} started for: {goal[:100]}")
        return pipeline_id

    def get_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline status."""
        pipeline = self._pipelines.get(pipeline_id)
        if pipeline:
            return pipeline.to_dict()
        return None

    def cancel(self, pipeline_id: str) -> bool:
        """Cancel a running pipeline."""
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline or pipeline.status not in (PipelineStatus.CREATED, PipelineStatus.RUNNING):
            return False

        # Cancel the async task
        task = self._tasks.get(pipeline_id)
        if task and not task.done():
            task.cancel()

        pipeline.status = PipelineStatus.CANCELLED
        for stage in pipeline.stages:
            if stage.status in (StageStatus.PENDING, StageStatus.RUNNING):
                stage.status = StageStatus.CANCELLED

        logger.info(f"Auto-Pilot pipeline {pipeline_id} cancelled")
        return True

    def list_pipelines(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List all pipelines (most recent first)."""
        sorted_pipes = sorted(
            self._pipelines.values(),
            key=lambda p: p.created_at,
            reverse=True,
        )
        return [p.to_dict() for p in sorted_pipes[:limit]]

    async def _run_pipeline(self, pipeline_id: str):
        """Execute pipeline stages sequentially."""
        pipeline = self._pipelines[pipeline_id]
        if pipeline.status == PipelineStatus.CANCELLED:
            return
        pipeline.status = PipelineStatus.RUNNING

        accumulated_context = f"Goal: {pipeline.goal}\n"

        try:
            for i, stage in enumerate(pipeline.stages):
                pipeline.current_stage_index = i
                stage.status = StageStatus.RUNNING
                stage.started_at = time.time()

                await self._broadcast_progress(pipeline)

                try:
                    result = await self._execute_stage(stage, accumulated_context)
                    stage.result = result
                    stage.status = StageStatus.COMPLETED
                    stage.completed_at = time.time()

                    # Add result to context for next stage
                    accumulated_context += (
                        f"\n--- {stage.name.upper()} Stage Result ---\n"
                        f"{result[:2000]}\n"
                    )

                    logger.info(
                        f"Pipeline {pipeline_id}: Stage '{stage.name}' completed "
                        f"in {(stage.completed_at - stage.started_at)*1000:.0f}ms"
                    )

                except asyncio.CancelledError:
                    stage.status = StageStatus.CANCELLED
                    raise
                except Exception as e:
                    stage.status = StageStatus.FAILED
                    stage.error = str(e)
                    stage.completed_at = time.time()
                    logger.error(
                        f"Pipeline {pipeline_id}: Stage '{stage.name}' failed: {e}"
                    )
                    # Continue to next stage despite failures (best-effort)
                    accumulated_context += (
                        f"\n--- {stage.name.upper()} Stage FAILED ---\n"
                        f"Error: {str(e)}\n"
                    )

                await self._broadcast_progress(pipeline)

            pipeline.status = PipelineStatus.COMPLETED
            pipeline.completed_at = time.time()

        except asyncio.CancelledError:
            pipeline.status = PipelineStatus.CANCELLED
            logger.info(f"Pipeline {pipeline_id} was cancelled")
        except Exception as e:
            pipeline.status = PipelineStatus.FAILED
            pipeline.error = str(e)
            pipeline.completed_at = time.time()
            logger.error(f"Pipeline {pipeline_id} failed: {e}")

        await self._broadcast_progress(pipeline)

    async def _execute_stage(
        self, stage: PipelineStage, context: str
    ) -> str:
        """Execute a single pipeline stage by delegating to the agent."""
        prompt = (
            f"You are working on the '{stage.name}' stage of an auto-pilot pipeline.\n"
            f"Your role: {stage.description}\n\n"
            f"Context from previous stages:\n{context}\n\n"
            f"Please complete this stage thoroughly."
        )

        if self.orchestrator and hasattr(self.orchestrator, 'process_request'):
            response = await self.orchestrator.process_request(prompt)
            return response.get("response", str(response))

        # Fallback: return a structured placeholder
        return (
            f"[{stage.name.upper()} STAGE] "
            f"Agent '{stage.agent_name}' would process: {stage.description}. "
            f"Orchestrator not available for live execution."
        )

    async def _broadcast_progress(self, pipeline: Pipeline):
        """Broadcast pipeline progress update via WebSocket or callback."""
        if self.broadcast_fn:
            try:
                await self.broadcast_fn({
                    "type": "autopilot_progress",
                    "pipeline": pipeline.to_dict(),
                })
            except Exception as e:
                logger.debug(f"Broadcast failed: {e}")
