"""
Tests for Auto-Pilot Pipeline (Feature A)
Tests pipeline creation, stage progression, cancellation, and status reporting.
"""

import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from autopilot import (
    AutoPilotPipeline,
    Pipeline,
    PipelineStage,
    PipelineStatus,
    StageStatus,
    DEFAULT_STAGES,
)


class MockOrchestrator:
    """Mock orchestrator that returns predictable responses."""

    def __init__(self, fail_stage=None):
        self.requests = []
        self.fail_stage = fail_stage

    async def process_request(self, request: str):
        self.requests.append(request)
        if self.fail_stage and self.fail_stage in request:
            raise RuntimeError(f"Simulated failure in stage")
        return {"response": f"Completed: {request[:80]}..."}


@pytest.fixture
def mock_orchestrator():
    return MockOrchestrator()


@pytest.fixture
def pipeline(mock_orchestrator):
    return AutoPilotPipeline(orchestrator=mock_orchestrator)


@pytest.fixture
def pipeline_no_orchestrator():
    return AutoPilotPipeline()


class TestPipelineCreation:
    def test_start_returns_pipeline_id(self, pipeline):
        pid = pipeline.start("Build a todo application with CRUD operations")
        assert pid is not None
        assert isinstance(pid, str)
        assert len(pid) > 0

    def test_start_creates_default_stages(self, pipeline):
        pid = pipeline.start("Build a REST API with authentication")
        status = pipeline.get_status(pid)
        assert status is not None
        assert len(status["stages"]) == len(DEFAULT_STAGES)

    def test_start_with_custom_stages(self, pipeline):
        custom = [
            ("analyze", "architect", "Analyze requirements"),
            ("code", "full-stack-developer", "Write code"),
        ]
        pid = pipeline.start("Quick task", stages=custom)
        status = pipeline.get_status(pid)
        assert len(status["stages"]) == 2
        assert status["stages"][0]["name"] == "analyze"

    def test_stage_names_match_defaults(self, pipeline):
        pid = pipeline.start("Build a todo application with CRUD operations")
        status = pipeline.get_status(pid)
        expected_names = [s[0] for s in DEFAULT_STAGES]
        actual_names = [s["name"] for s in status["stages"]]
        assert actual_names == expected_names

    def test_pipeline_has_goal(self, pipeline):
        goal = "Build a microservice architecture"
        pid = pipeline.start(goal)
        status = pipeline.get_status(pid)
        assert status["goal"] == goal


class TestPipelineStatus:
    def test_get_status_returns_dict(self, pipeline):
        pid = pipeline.start("Build a todo application with CRUD operations")
        status = pipeline.get_status(pid)
        assert isinstance(status, dict)
        assert "id" in status
        assert "goal" in status
        assert "stages" in status
        assert "progress_pct" in status

    def test_get_status_unknown_id_returns_none(self, pipeline):
        assert pipeline.get_status("nonexistent") is None

    def test_initial_progress_is_zero(self, pipeline):
        pid = pipeline.start("Build a todo application with CRUD operations")
        status = pipeline.get_status(pid)
        assert status["progress_pct"] == 0

    def test_stage_structure(self, pipeline):
        pid = pipeline.start("Build a todo application with CRUD operations")
        status = pipeline.get_status(pid)
        stage = status["stages"][0]
        assert "name" in stage
        assert "agent_name" in stage
        assert "description" in stage
        assert "status" in stage
        assert stage["status"] == "pending"


class TestPipelineExecution:
    @pytest.mark.asyncio
    async def test_pipeline_completes_all_stages(self, mock_orchestrator):
        ap = AutoPilotPipeline(orchestrator=mock_orchestrator)
        pid = ap.start("Build a simple calculator app")

        # Wait for pipeline to complete
        for _ in range(50):
            await asyncio.sleep(0.1)
            status = ap.get_status(pid)
            if status["status"] in ("completed", "failed"):
                break

        status = ap.get_status(pid)
        assert status["status"] == "completed"
        assert status["progress_pct"] == 100

    @pytest.mark.asyncio
    async def test_stages_run_sequentially(self, mock_orchestrator):
        ap = AutoPilotPipeline(orchestrator=mock_orchestrator)
        pid = ap.start("Build a simple calculator app")

        for _ in range(50):
            await asyncio.sleep(0.1)
            status = ap.get_status(pid)
            if status["status"] in ("completed", "failed"):
                break

        # All stages should be completed
        for stage in ap.get_status(pid)["stages"]:
            assert stage["status"] == "completed"

    @pytest.mark.asyncio
    async def test_orchestrator_receives_requests(self, mock_orchestrator):
        ap = AutoPilotPipeline(orchestrator=mock_orchestrator)
        pid = ap.start("Build a simple calculator app")

        for _ in range(50):
            await asyncio.sleep(0.1)
            if ap.get_status(pid)["status"] == "completed":
                break

        # Orchestrator should have received one request per stage
        assert len(mock_orchestrator.requests) == len(DEFAULT_STAGES)

    @pytest.mark.asyncio
    async def test_pipeline_without_orchestrator_uses_fallback(self):
        ap = AutoPilotPipeline()

        custom = [("quick", "dev", "Quick check")]
        pid = ap.start("Simple task with no orchestrator", stages=custom)

        for _ in range(30):
            await asyncio.sleep(0.1)
            if ap.get_status(pid)["status"] == "completed":
                break

        status = ap.get_status(pid)
        assert status["status"] == "completed"
        assert "Orchestrator not available" in status["stages"][0].get("result_preview", "")

    @pytest.mark.asyncio
    async def test_stage_failure_continues_pipeline(self):
        """Pipeline should continue even if a stage fails."""
        orch = MockOrchestrator(fail_stage="review")
        ap = AutoPilotPipeline(orchestrator=orch)
        pid = ap.start("Build a simple calculator app")

        for _ in range(50):
            await asyncio.sleep(0.1)
            status = ap.get_status(pid)
            if status["status"] in ("completed", "failed"):
                break

        status = ap.get_status(pid)
        # Pipeline should still complete (best-effort)
        assert status["status"] == "completed"

        # The review stage should be marked failed
        review_stage = next(s for s in status["stages"] if s["name"] == "review")
        assert review_stage["status"] == "failed"
        assert review_stage["error"] is not None


class TestPipelineCancellation:
    @pytest.mark.asyncio
    async def test_cancel_running_pipeline(self, mock_orchestrator):
        ap = AutoPilotPipeline(orchestrator=mock_orchestrator)
        pid = ap.start("Build a complex machine learning pipeline application")

        # Give it a moment to start
        await asyncio.sleep(0.05)

        success = ap.cancel(pid)
        assert success is True

        status = ap.get_status(pid)
        assert status["status"] == "cancelled"

    def test_cancel_nonexistent_returns_false(self, pipeline):
        assert pipeline.cancel("nonexistent") is False


class TestPipelineHistory:
    def test_list_empty(self, pipeline):
        assert pipeline.list_pipelines() == []

    def test_list_returns_created_pipelines(self, pipeline):
        pipeline.start("Goal A - build something")
        pipeline.start("Goal B - build another")
        result = pipeline.list_pipelines()
        assert len(result) == 2

    def test_list_respects_limit(self, pipeline):
        for i in range(5):
            pipeline.start(f"Goal {i} - build something cool")
        result = pipeline.list_pipelines(limit=3)
        assert len(result) == 3

    def test_list_most_recent_first(self, pipeline):
        pipeline.start("First goal to build")
        pipeline.start("Second goal to build")
        result = pipeline.list_pipelines()
        assert result[0]["goal"] == "Second goal to build"


class TestPipelineDataClasses:
    def test_pipeline_stage_to_dict(self):
        stage = PipelineStage(
            name="plan", agent_name="architect", description="Create plan"
        )
        d = stage.to_dict()
        assert d["name"] == "plan"
        assert d["status"] == "pending"
        assert d["duration_ms"] is None

    def test_pipeline_stage_duration(self):
        stage = PipelineStage(
            name="plan",
            agent_name="architect",
            description="Create plan",
            started_at=100.0,
            completed_at=100.5,
            status=StageStatus.COMPLETED,
        )
        d = stage.to_dict()
        assert d["duration_ms"] == 500.0

    def test_pipeline_to_dict(self):
        p = Pipeline(id="test-1", goal="Build an app")
        d = p.to_dict()
        assert d["id"] == "test-1"
        assert d["progress_pct"] == 0

    def test_pipeline_progress_calculation(self):
        p = Pipeline(
            id="test-2",
            goal="Build an app",
            stages=[
                PipelineStage("a", "agent1", "d1", status=StageStatus.COMPLETED),
                PipelineStage("b", "agent2", "d2", status=StageStatus.COMPLETED),
                PipelineStage("c", "agent3", "d3", status=StageStatus.PENDING),
                PipelineStage("d", "agent4", "d4", status=StageStatus.PENDING),
            ],
        )
        assert p._progress_pct() == 50
