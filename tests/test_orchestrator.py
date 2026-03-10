import pytest
from unittest.mock import MagicMock, call
from src.orchestrator import OrchestrationEngine
from src.models import ExperimentInput, MediaType, Decision, ExperimentStatus


@pytest.fixture
def mock_clients():
    ai_service = MagicMock()
    supabase = MagicMock()

    # Setup happy path returns
    ai_service.run_model.return_value = {
        "raw_output": "test_output",
        "latency_ms": 100,
        "cost_usd": 0.01
    }

    ai_service.evaluate_output.return_value = {
        "scores": [{"metric_name": "quality", "score": 1.0, "reasoning": "perfect"}]
    }

    ai_service.compare_models.return_value = {
        "winning_model": "model_a",
        "reason": "better",
        "tradeoffs": {"none": "none"}
    }

    supabase.create_experiment.return_value = "exp_123"

    return ai_service, supabase


def test_create_experiment(mock_clients):
    ai_service, supabase = mock_clients
    engine = OrchestrationEngine(ai_service, supabase)

    exp_id = engine.create_experiment("media_1")

    assert exp_id == "exp_123"
    supabase.create_experiment.assert_called_with("media_1")
    supabase.update_experiment_status.assert_called_with("exp_123", ExperimentStatus.RUNNING)


def test_run_experiment_flow_happy_path(mock_clients):
    ai_service, supabase = mock_clients
    engine = OrchestrationEngine(ai_service, supabase)

    input_data = ExperimentInput(
        media_id="media_1",
        media_type=MediaType.AUDIO,
        model_list=["model_a", "model_b"],
        user_api_keys={"model_a": "key1", "model_b": "key2"}
    )

    engine.run_experiment_flow("exp_123", input_data, text_input="test transcript")

    # Check calls
    assert ai_service.run_model.call_count == 2
    assert supabase.insert_model_run.call_count == 2

    assert ai_service.evaluate_output.call_count == 2
    assert supabase.insert_eval_metrics.call_count == 2

    ai_service.compare_models.assert_called_once()
    supabase.update_experiment_recommendation.assert_called_once()

    # After successful flow, status should be updated to AWAITING_DECISION
    supabase.update_experiment_status.assert_called_with("exp_123", ExperimentStatus.AWAITING_DECISION)


def test_max_models_validation(mock_clients):
    ai_service, supabase = mock_clients
    engine = OrchestrationEngine(ai_service, supabase)

    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        input_data = ExperimentInput(
            media_id="media_1",
            media_type=MediaType.AUDIO,
            model_list=["a", "b", "c", "d"],  # 4 models — exceeds max_length=3
            user_api_keys={}
        )


def test_workflow_single_model_failure_still_completes(mock_clients):
    """When a model fails, orchestrator persists the error and still runs comparison."""
    ai_service, supabase = mock_clients
    engine = OrchestrationEngine(ai_service, supabase)

    # Simulate API failure
    ai_service.run_model.side_effect = Exception("API Down")

    input_data = ExperimentInput(
        media_id="media_1",
        media_type=MediaType.AUDIO,
        model_list=["model_a"],
        user_api_keys={"model_a": "key1"}
    )

    # Orchestrator catches individual model failures, persists them, and continues
    engine.run_experiment_flow("exp_123", input_data, text_input="test transcript")

    # Failed run should still be persisted
    supabase.insert_model_run.assert_called_once()
    supabase.insert_eval_metrics.assert_called_once()

    # Comparison still runs with the failed run data
    ai_service.compare_models.assert_called_once()

    # Status ends at AWAITING_DECISION (not FAILED)
    supabase.update_experiment_status.assert_called_with("exp_123", ExperimentStatus.AWAITING_DECISION)


def test_submit_human_decision(mock_clients):
    ai_service, supabase = mock_clients
    engine = OrchestrationEngine(ai_service, supabase)

    engine.submit_human_decision("exp_123", Decision.SHIP, "It is good")

    supabase.update_experiment_decision.assert_called_with("exp_123", Decision.SHIP, "It is good")
    supabase.update_experiment_status.assert_called_with("exp_123", ExperimentStatus.COMPLETE)
