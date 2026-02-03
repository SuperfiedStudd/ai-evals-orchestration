import pytest
from unittest.mock import MagicMock, call
from src.orchestrator import OrchestrationEngine
from src.models import ExperimentInput, MediaType, Decision, ExperimentStatus

@pytest.fixture
def mock_clients():
    fast_api = MagicMock()
    supabase = MagicMock()
    
    # Setup happy path returns
    fast_api.run_model.return_value = {
        "raw_output": "test_output",
        "latency_ms": 100,
        "cost_usd": 0.01
    }
    
    fast_api.evaluate_output.return_value = {
        "scores": [{"metric_name": "quality", "score": 1.0, "reasoning": "perfect"}]
    }
    
    fast_api.compare_models.return_value = {
        "winning_model": "model_a",
        "reason": "better",
        "tradeoffs": ["none"]
    }
    
    supabase.create_experiment.return_value = "exp_123"
    
    return fast_api, supabase

def test_create_experiment(mock_clients):
    fast_api, supabase = mock_clients
    engine = OrchestrationEngine(fast_api, supabase)
    
    exp_id = engine.create_experiment("media_1")
    
    assert exp_id == "exp_123"
    supabase.create_experiment.assert_called_with("media_1")
    supabase.update_experiment_status.assert_called_with("exp_123", ExperimentStatus.RUNNING)

def test_run_experiment_flow_happy_path(mock_clients):
    fast_api, supabase = mock_clients
    engine = OrchestrationEngine(fast_api, supabase)
    
    input_data = ExperimentInput(
        media_id="media_1",
        media_type=MediaType.AUDIO,
        model_list=["model_a", "model_b"],
        user_api_keys={"model_a": "key1", "model_b": "key2"}
    )
    
    engine.run_experiment_flow("exp_123", input_data)
    
    # Check calls
    assert fast_api.run_model.call_count == 2
    assert supabase.insert_model_run.call_count == 2
    
    assert fast_api.evaluate_output.call_count == 2
    assert supabase.insert_eval_metrics.call_count == 2
    
    fast_api.compare_models.assert_called_once()
    supabase.update_experiment_recommendation.assert_called_once()
    
    # Ensure no failure update
    supabase.update_experiment_status.assert_not_called()

def test_max_models_validation(mock_clients):
    fast_api, supabase = mock_clients
    engine = OrchestrationEngine(fast_api, supabase)
    
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError):
        input_data = ExperimentInput(
            media_id="media_1",
            media_type=MediaType.AUDIO,
            model_list=["a", "b", "c", "d"], # 4 models
            user_api_keys={}
        )


def test_workflow_failure_updates_status(mock_clients):
    fast_api, supabase = mock_clients
    engine = OrchestrationEngine(fast_api, supabase)
    
    # Simulate API failure
    fast_api.run_model.side_effect = Exception("API Down")
    
    input_data = ExperimentInput(
        media_id="media_1",
        media_type=MediaType.AUDIO,
        model_list=["model_a"],
        user_api_keys={}
    )
    
    with pytest.raises(Exception, match="API Down"):
        engine.run_experiment_flow("exp_123", input_data)
        
    supabase.update_experiment_status.assert_called_with(
        "exp_123", ExperimentStatus.FAILED, error="API Down"
    )

def test_submit_human_decision(mock_clients):
    fast_api, supabase = mock_clients
    engine = OrchestrationEngine(fast_api, supabase)
    
    engine.submit_human_decision("exp_123", Decision.SHIP, "It is good")
    
    supabase.update_experiment_decision.assert_called_with("exp_123", Decision.SHIP, "It is good")
    supabase.update_experiment_status.assert_called_with("exp_123", ExperimentStatus.COMPLETE)
