import uuid
from typing import List, Dict, Any
from .models import (
    ExperimentInput, ModelRunResult, EvaluationResult, ComparisonResult,
    ExperimentStatus, Decision, EvaluationScore
)
from .services import AIProviderService, SupabaseClient

FIXED_PROMPT = """
You are an expert editor. Please edit the following transcript for clarity, conciseness, and impact.
Maintain the original meaning but improve the flow.
"""

class OrchestrationEngine:
    def __init__(self, ai_service: AIProviderService = None, supabase_client: SupabaseClient = None):
        self.ai = ai_service or AIProviderService()
        self.supabase = supabase_client or SupabaseClient()

    def create_experiment(self, media_id_or_name: str) -> str:
        """
        Step 1: Create experiment in Supabase.
        """
        experiment_id = self.supabase.create_experiment(media_id_or_name)
        self.supabase.update_experiment_status(experiment_id, ExperimentStatus.RUNNING)
        return experiment_id

    def run_experiment_flow(self, experiment_id: str, input_data: ExperimentInput, file_path: str = None, text_input: str = None):
        """
        Executes the core automated flow: Transcribe -> Run Models -> Evaluate -> Compare.
        """
        if len(input_data.model_list) > 3:
            raise ValueError("Max 3 models allowed per experiment.")
        
        try:
            # Phase 0: Transcription
            transcript = text_input
            if not transcript and file_path:
                print(f"Transcribing file: {file_path}")
                transcription_result = self.ai.transcribe_audio(file_path)
                transcript = transcription_result["transcript"]
                # We could log transcription cost/latency here if we had a table for it
            
            if not transcript:
                raise ValueError("No transcript available (neither text input nor audio file provided).")

            run_results_map = {} # run_id -> raw_output
            run_ids = []
            runs_data_for_comparison = []
            
            # Phase 1: Run Models
            failed_models = []
            
            for model_name in input_data.model_list:
                api_key = input_data.user_api_keys.get(model_name, "")
                
                # Identify provider (simple check)
                provider = "openai"
                if "claude" in model_name.lower(): provider = "anthropic"
                # Removed google check
                
                model_config = {
                    "name": model_name,
                    "provider": provider,
                    "api_key": api_key
                }

                try:
                    result_data = self.ai.run_model(transcript, model_config, FIXED_PROMPT)
                except Exception as e:
                    print(f"Error running model {model_name}: {e}")
                    failed_models.append(model_name)
                    
                    # Persist failed run so it shows in UI
                    try:
                        run_id = str(uuid.uuid4())
                        run_result = ModelRunResult(
                            run_id=run_id,
                            experiment_id=experiment_id,
                            model_name=model_name,
                            raw_output=f"ERROR: {str(e)}",
                            latency_ms=0,
                            cost_usd=0.0
                        )
                        self.supabase.insert_model_run(run_result)
                        
                        # Insert failed metrics
                        eval_result = EvaluationResult(
                            eval_id=str(uuid.uuid4()),
                            run_id=run_id,
                            scores=[
                                EvaluationScore(metric_name="edit_quality", score=0, reasoning="Model execution failed"),
                                EvaluationScore(metric_name="structural_clarity", score=0, reasoning=f"Error: {str(e)}"),
                                EvaluationScore(metric_name="publish_ready", score=0, reasoning="Failed")
                            ]
                        )
                        self.supabase.insert_eval_metrics(eval_result)
                        
                        # Add to comparison data
                        runs_data_for_comparison.append({
                            "model_name": model_name,
                            "scores": [s.model_dump() for s in eval_result.scores],
                            "latency_ms": 0,
                            "cost_usd": 0
                        })

                    except Exception as persist_err:
                         print(f"Failed to persist error record for {model_name}: {persist_err}")

                    continue # CONTINUE TO NEXT MODEL

                # --- SUCCESS PATH ---
                run_id = str(uuid.uuid4())
                run_result = ModelRunResult(
                    run_id=run_id,
                    experiment_id=experiment_id,
                    model_name=result_data.get("model_name", model_name), 
                    raw_output=result_data["raw_output"],
                    latency_ms=result_data["latency_ms"],
                    cost_usd=result_data["cost_usd"]
                )
                self.supabase.insert_model_run(run_result)
                run_ids.append(run_id)
                run_results_map[run_id] = result_data["raw_output"]
                
                # --- EVALUATE IMMEDIATELY ---
                eval_data = self.ai.evaluate_output(result_data["raw_output"])
                
                eval_id = str(uuid.uuid4())
                scores = [EvaluationScore(**s) for s in eval_data["scores"]]
                
                eval_result = EvaluationResult(
                    eval_id=eval_id,
                    run_id=run_id,
                    scores=scores
                )
                self.supabase.insert_eval_metrics(eval_result)
                
                # Add to comparison data
                runs_data_for_comparison.append({
                    "model_name": result_data.get("model_name", model_name),
                    "scores": eval_data["scores"], # List of dicts, correct
                    "latency_ms": result_data["latency_ms"],
                    "cost_usd": result_data["cost_usd"]
                })

            if not runs_data_for_comparison:
                raise RuntimeError(f"All models failed to process. Errors: {failed_models}")
            comparison_data = self.ai.compare_models(runs_data_for_comparison)
            print(f"[Orchestrator] Comparison Data: {comparison_data}")
            
            comparison_result = ComparisonResult(
                experiment_id=experiment_id,
                winning_model=comparison_data["winning_model"],
                reason=comparison_data["reason"],
                tradeoffs=comparison_data.get("tradeoffs", {})
            )
            self.supabase.update_experiment_recommendation(comparison_result)
            
            # Update status to AWAITING_DECISION
            self.supabase.update_experiment_status(experiment_id, ExperimentStatus.AWAITING_DECISION)
             
        except Exception as e:
            print(f"Workflow failed: {e}")
            self.supabase.update_experiment_status(experiment_id, ExperimentStatus.FAILED, error=str(e))
            raise e

    def submit_human_decision(self, experiment_id: str, decision: Decision, reason: str):
        """
        Step 4: Accept human decision and mark complete.
        """
        self.supabase.update_experiment_decision(experiment_id, decision, reason)
        self.supabase.update_experiment_status(experiment_id, ExperimentStatus.COMPLETE)


