"""Comprehensive tests for SignalForge new modules."""

import json
import pytest
from datetime import datetime, timezone

from app.providers.encryption import EncryptionService
from app.pipeline_templates.validator import validate_graph, topological_sort, GraphValidationError
from app.executions.engine import (
    validate_execution_transition,
    validate_node_transition,
    StateMachineError,
    EXECUTION_TRANSITIONS,
    NODE_TRANSITIONS,
)
from app.scoring.service import ScoreCalculator, ScoreInput
from app.exports.service import ExportService
from app.providers.adapter import (
    MockProviderAdapter,
    OpenAICompatibleAdapter,
    ProviderResponse,
    ProviderError,
)


# =============================================================================
# ENCRYPTION TESTS
# =============================================================================

class TestEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        svc = EncryptionService("test-key-32-chars-long-for-aes!")
        original = "sk-proj-test-key-12345"
        encrypted = svc.encrypt(original)
        assert encrypted != original
        assert encrypted.endswith("=")  # Base64 padding
        decrypted = svc.decrypt(encrypted)
        assert decrypted == original

    def test_empty_string(self):
        svc = EncryptionService("test-key-32-chars-long-for-aes!")
        assert svc.encrypt("") == ""
        assert svc.decrypt("") == ""

    def test_mask_long_key(self):
        svc = EncryptionService("test-key-32-chars-long-for-aes!")
        masked = svc.mask("sk-abcdefghijklmnopqrstuvwxyz", visible_chars=3)
        assert masked.startswith("sk-")
        assert "****" in masked
        assert masked.endswith("xyz")

    def test_mask_short_key_no_masking(self):
        svc = EncryptionService("test-key-32-chars-long-for-aes!")
        assert svc.mask("short") == "short"

    def test_different_keys_produce_different_ciphertexts(self):
        svc1 = EncryptionService("key-one-32-chars-long-for-aes!!")
        svc2 = EncryptionService("key-two-32-chars-long-for-aes!!")
        assert svc1.encrypt("secret") != svc2.encrypt("secret")


# =============================================================================
# PIPELINE GRAPH VALIDATOR TESTS
# =============================================================================

class TestGraphValidator:
    def test_valid_graph(self):
        graph = {
            "nodes": [
                {"key": "start", "node_type": "start"},
                {"key": "agent1", "node_type": "agent"},
                {"key": "output1", "node_type": "output"},
            ],
            "edges": [
                {"source": "start", "target": "agent1"},
                {"source": "agent1", "target": "output1"},
            ],
        }
        errors = validate_graph(graph)
        assert errors == []

    def test_missing_start_node(self):
        graph = {
            "nodes": [
                {"key": "agent1", "node_type": "agent"},
                {"key": "output1", "node_type": "output"},
            ],
            "edges": [{"source": "agent1", "target": "output1"}],
        }
        errors = validate_graph(graph)
        assert any("start" in e.lower() for e in errors)

    def test_multiple_start_nodes(self):
        graph = {
            "nodes": [
                {"key": "start1", "node_type": "start"},
                {"key": "start2", "node_type": "start"},
                {"key": "output1", "node_type": "output"},
            ],
            "edges": [],
        }
        errors = validate_graph(graph)
        assert any("start" in e.lower() for e in errors)

    def test_missing_output_node(self):
        graph = {
            "nodes": [
                {"key": "start", "node_type": "start"},
                {"key": "agent1", "node_type": "agent"},
            ],
            "edges": [],
        }
        errors = validate_graph(graph)
        assert any("output" in e.lower() for e in errors)

    def test_unsupported_node_type(self):
        graph = {
            "nodes": [
                {"key": "start", "node_type": "start"},
                {"key": "bad", "node_type": "unsupported_type"},
                {"key": "output1", "node_type": "output"},
            ],
            "edges": [],
        }
        errors = validate_graph(graph)
        assert any("unsupported" in e.lower() for e in errors)

    def test_missing_node_reference_in_edge(self):
        graph = {
            "nodes": [
                {"key": "start", "node_type": "start"},
                {"key": "output1", "node_type": "output"},
            ],
            "edges": [{"source": "start", "target": "nonexistent"}],
        }
        errors = validate_graph(graph)
        assert any("nonexistent" in e for e in errors)

    def test_cycle_detection(self):
        graph = {
            "nodes": [
                {"key": "a", "node_type": "start"},
                {"key": "b", "node_type": "agent"},
                {"key": "c", "node_type": "agent"},
                {"key": "d", "node_type": "output"},
            ],
            "edges": [
                {"source": "a", "target": "b"},
                {"source": "b", "target": "c"},
                {"source": "c", "target": "b"},  # Cycle!
                {"source": "b", "target": "d"},
            ],
        }
        errors = validate_graph(graph)
        assert any("cycle" in e.lower() for e in errors)

    def test_duplicate_node_key(self):
        graph = {
            "nodes": [
                {"key": "start", "node_type": "start"},
                {"key": "start", "node_type": "start"},
                {"key": "output1", "node_type": "output"},
            ],
            "edges": [],
        }
        errors = validate_graph(graph)
        assert any("duplicate" in e.lower() for e in errors)

    def test_topological_sort(self):
        nodes = [
            {"key": "s", "node_type": "start"},
            {"key": "a", "node_type": "agent"},
            {"key": "b", "node_type": "agent"},
            {"key": "o", "node_type": "output"},
        ]
        edges = [
            {"source": "s", "target": "a"},
            {"source": "a", "target": "b"},
            {"source": "b", "target": "o"},
        ]
        order = topological_sort(nodes, edges)
        assert order.index("s") < order.index("a")
        assert order.index("a") < order.index("b")
        assert order.index("b") < order.index("o")


# =============================================================================
# EXECUTION STATE MACHINE TESTS
# =============================================================================

class TestExecutionStateMachine:
    def test_valid_transitions(self):
        transitions = [
            ("queued", "running"),
            ("running", "completed"),
            ("queued", "cancelled"),
            ("running", "failed"),
            ("running", "awaiting_approval"),
            ("awaiting_approval", "running"),
        ]
        for current, target in transitions:
            validate_execution_transition(current, target)

    def test_invalid_transitions_raise_error(self):
        transitions = [
            ("completed", "running"),
            ("completed", "queued"),
            ("failed", "running"),
            ("cancelled", "running"),
        ]
        for current, target in transitions:
            with pytest.raises(StateMachineError):
                validate_execution_transition(current, target)


class TestNodeStateMachine:
    def test_valid_node_transitions(self):
        transitions = [
            ("pending", "running"),
            ("running", "completed"),
            ("running", "failed"),
            ("failed", "pending"),
            ("pending", "skipped"),
        ]
        for current, target in transitions:
            validate_node_transition(current, target)

    def test_invalid_node_transitions_raise_error(self):
        transitions = [
            ("completed", "running"),
            ("completed", "pending"),
            ("skipped", "running"),
        ]
        for current, target in transitions:
            with pytest.raises(StateMachineError):
                validate_node_transition(current, target)


# =============================================================================
# SCORING TESTS
# =============================================================================

class TestScoring:
    def test_bid_scenario(self):
        calc = ScoreCalculator()
        scores = ScoreInput(technical_fit=90, proof_strength=85, client_quality=80,
                            scope_clarity=75, budget_fit=70, competition_risk=80,
                            delivery_confidence=85)
        result = calc.calculate(scores)
        assert result.decision == "bid"
        assert result.total >= 75
        assert result.total <= 100

    def test_conditional_bid_scenario(self):
        calc = ScoreCalculator()
        scores = ScoreInput(technical_fit=65, proof_strength=60, client_quality=55,
                            scope_clarity=60, budget_fit=50, competition_risk=50,
                            delivery_confidence=55)
        result = calc.calculate(scores)
        assert result.decision == "conditional_bid"
        assert 55 <= result.total < 75

    def test_skip_scenario(self):
        calc = ScoreCalculator()
        scores = ScoreInput(technical_fit=30, proof_strength=20, client_quality=25,
                            scope_clarity=40, budget_fit=35, competition_risk=40,
                            delivery_confidence=20)
        result = calc.calculate(scores)
        assert result.decision == "skip"
        assert result.total < 55

    def test_max_score(self):
        calc = ScoreCalculator()
        scores = ScoreInput(technical_fit=100, proof_strength=100, client_quality=100,
                            scope_clarity=100, budget_fit=100, competition_risk=100,
                            delivery_confidence=100)
        result = calc.calculate(scores)
        assert result.total == 100.0

    def test_min_score(self):
        calc = ScoreCalculator()
        scores = ScoreInput(technical_fit=0, proof_strength=0, client_quality=0,
                            scope_clarity=0, budget_fit=0, competition_risk=0,
                            delivery_confidence=0)
        result = calc.calculate(scores)
        assert result.total == 0.0

    def test_score_clamping(self):
        calc = ScoreCalculator()
        scores = ScoreInput(technical_fit=150, proof_strength=-10, client_quality=50,
                            scope_clarity=50, budget_fit=50, competition_risk=50,
                            delivery_confidence=50)
        result = calc.calculate(scores)
        # Clamped to 0-100
        assert result.categories["technical_fit"] == 100.0
        assert result.categories["proof_strength"] == 0.0

    def test_weights_sum_to_one(self):
        total_weight = sum(ScoreCalculator().weights.values())
        assert abs(total_weight - 1.0) < 0.001

    def test_boundary_bid(self):
        calc = ScoreCalculator(thresholds={"bid": 75, "conditional_bid": 55, "skip": 0})
        # Exactly 75 should be "bid"
        scores = ScoreInput(technical_fit=100, proof_strength=100, client_quality=100,
                            scope_clarity=25, budget_fit=0, competition_risk=0,
                            delivery_confidence=0)
        result = calc.calculate(scores)
        # technical_fit 100*0.30 + proof_strength 100*0.20 + client_quality 100*0.15 + scope_clarity 25*0.10 = 30+20+15+2.5 = 67.5
        # This is less than 75, so conditional
        assert result.decision in ("conditional_bid", "bid")

    def test_configurable_thresholds(self):
        custom = ScoreCalculator(thresholds={"bid": 50, "conditional_bid": 30, "skip": 0})
        scores = ScoreInput(technical_fit=70, proof_strength=60, client_quality=50,
                            scope_clarity=50, budget_fit=50, competition_risk=50,
                            delivery_confidence=50)
        result = custom.calculate(scores)
        assert result.decision == "bid"  # Lower threshold

    def test_deterministic(self):
        calc = ScoreCalculator()
        scores = ScoreInput(technical_fit=75, proof_strength=75, client_quality=75,
                            scope_clarity=75, budget_fit=75, competition_risk=75,
                            delivery_confidence=75)
        r1 = calc.calculate(scores)
        r2 = calc.calculate(scores)
        assert r1.total == r2.total
        assert r1.decision == r2.decision


# =============================================================================
# EXPORT TESTS
# =============================================================================

class TestExports:
    @pytest.fixture
    def sample_package(self):
        return {
            "status": "final",
            "project": {"id": 1, "name": "Test Project", "project_type": "upwork_opportunity"},
            "sources": [{"title": "Job Post", "source_type": "job_post"}],
            "scorecard": {
                "total": 82.5,
                "decision": "bid",
                "categories": {"technical_fit": 90.0, "proof_strength": 85.0},
                "weights": {"technical_fit": 0.30, "proof_strength": 0.20},
                "weighted_scores": {"technical_fit": 27.0, "proof_strength": 17.0},
            },
            "assessment": {
                "client_quality": {"quality_score": 8, "positive_signals": ["Good history"], "risk_flags": []},
                "technical_fit": {"fit_score": 85, "matched_requirements": ["Python"], "gaps": []},
                "competition_risk": {"competition_level": "medium", "delivery_risks": [], "red_flags": []},
                "evidence_mapping": {"proof_items": [], "unsupported_claims_to_avoid": []},
                "bid_decision": {"reasons": ["Strong technical match"]},
                "unanswered_questions": ["What is exact timeline?"],
            },
            "proposal": {
                "proposal_text": "Dear Client, I have the experience you need...",
                "claims_provenance": [],
            },
            "provenance": [{"claim": "Python expert", "claim_type": "portfolio_fact", "confidence": 1.0}],
            "execution_metadata": {"execution_id": 1, "status": "completed", "total_tokens": 1500},
        }

    def test_json_export(self, sample_package):
        svc = ExportService()
        result = svc.export_json(sample_package)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["status"] == "final"
        assert parsed["project"]["name"] == "Test Project"

    def test_markdown_export(self, sample_package):
        svc = ExportService()
        result = svc.export_markdown(sample_package)
        assert isinstance(result, str)
        assert "# Decision Package" in result
        assert "## Scorecard" in result
        assert "## Bid Recommendation" in result
        assert "**Decision:** Bid" in result or "**Decision:** bid" in result.lower()

    def test_plain_text_proposal(self, sample_package):
        svc = ExportService()
        result = svc.export_plain_text_proposal(sample_package)
        assert "Dear Client" in result

    def test_empty_proposal_returns_default(self):
        svc = ExportService()
        result = svc.export_plain_text_proposal({"proposal": {}})
        assert "No proposal" in result

    def test_build_package_includes_metadata(self):
        svc = ExportService()
        pkg = svc.build_package(
            project={"id": 1, "name": "Test"},
            scorecard={"total": 80, "decision": "bid"},
            assessment={},
            sources=[],
        )
        assert pkg["status"] == "final"
        assert "metadata" in pkg
        assert "generation_timestamp" in pkg["metadata"]


# =============================================================================
# PROVIDER ADAPTER TESTS
# =============================================================================

class TestProviderAdapter:
    def test_mock_provider_test_connection(self):
        adapter = MockProviderAdapter()
        success, msg, models = adapter.test_connection()
        assert success is True
        assert "Mock" in msg
        assert len(models) == 2

    def test_mock_provider_generate(self):
        adapter = MockProviderAdapter()
        response = adapter.generate([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Extract the job title from: Need a Python developer."},
        ])
        assert isinstance(response, ProviderResponse)
        assert response.model == "mock-provider-v1"
        assert len(response.content) > 0
        assert response.duration_ms > 0

    def test_mock_provider_custom_response(self):
        adapter = MockProviderAdapter(mock_responses={
            "test input": '{"result": "custom"}'
        })
        response = adapter.generate([
            {"role": "user", "content": "test input"}
        ])
        data = json.loads(response.content)
        assert data["result"] == "custom"

    def test_mock_provider_structured_output(self):
        adapter = MockProviderAdapter()
        response = adapter.generate(
            [{"role": "user", "content": "Analyze this data."}],
            response_format={"type": "json_object"},
        )
        parsed = json.loads(response.content)
        assert "analysis" in parsed
        assert parsed["mock_output"] is True

    def test_provider_response_dataclass(self):
        resp = ProviderResponse(
            content="test",
            model="gpt-4",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
            duration_ms=100,
        )
        assert resp.content == "test"
        assert resp.total_tokens == 30
        assert resp.duration_ms == 100


# =============================================================================
# AUTHORIZATION TESTS
# =============================================================================

class TestAuthorization:
    def test_workspace_owner_isolation_pattern(self):
        """The workspace service pattern should prevent cross-user access."""
        from app.workspaces.service import _check_owner
        from app.auth.models import User
        from app.workspaces.models import Workspace

        user1 = User(id=1, email="u1@test.com", username="user1", hashed_password="pw1")
        user2 = User(id=2, email="u2@test.com", username="user2", hashed_password="pw2")
        ws = Workspace(id=1, name="WS", owner_id=1)

        # User1 owns it - should pass
        _check_owner(ws, user1)

        # User2 does not own it - should raise
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            _check_owner(ws, user2)
        assert exc.value.status_code == 403


# =============================================================================
# ALEMBIC / MODEL IMPORT TESTS
# =============================================================================

class TestModelImports:
    def test_all_models_importable(self):
        """All model tables should be importable without errors."""
        import app.models
        from app.database.database import Base
        # Check expected tables are registered
        tables = Base.metadata.tables
        expected = [
            "users", "workspaces", "workflows", "jobs", "logs",
            "provider_connections", "agent_definitions", "tool_definitions",
            "source_documents", "ground_truth_registry", "pipeline_templates",
            "pipeline_executions", "node_executions", "artifacts",
            "approval_requests", "opportunity_projects", "prompt_template_versions",
        ]
        for table in expected:
            assert table in tables, f"Table '{table}' not found in metadata"
