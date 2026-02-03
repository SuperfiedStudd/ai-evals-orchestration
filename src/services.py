import os
import json
import time
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_fixed
from .models import ModelRunResult, EvaluationResult, ComparisonResult, ExperimentStatus, Decision
from supabase import create_client, Client
from dotenv import load_dotenv

import openai
import anthropic

load_dotenv()

class AIProviderService:
    """
    Real AI Provider Service that connects to OpenAI/Anthropic.
    Also handles Transcription via OpenAI Whisper.
    """

    def __init__(self):
        # Server-side key for transcription
        self.server_openai_key = os.getenv("OPENAI_API_KEY") 
        if not self.server_openai_key:
            print("WARNING: OPENAI_API_KEY not set in env. Transcription will fail.")

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    def transcribe_audio(self, file_path: str) -> Dict[str, Any]:
        """
        Transcribes audio using OpenAI Whisper.
        """
        if not self.server_openai_key:
            raise ValueError("OPENAI_API_KEY not set on server for transcription.")
        
        client = openai.OpenAI(api_key=self.server_openai_key)
        
        start_time = time.time()
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        
        latency = int((time.time() - start_time) * 1000)
        
        return {
            "transcript": transcript.text,
            "latency_ms": latency,
            "cost_usd": 0.006 * (latency / 60000) # Rough estimate $0.006/min
        }

    # Removed retry decorator to allow Orchestrator to handle individual failures without excessive waiting
    def run_model(self, transcript: str, model_config: Dict[str, str], prompt_template: str) -> Dict[str, Any]:
        """
        Runs the model with the given config and prompt.
        model_config: { "name": "gpt-4o", "provider": "openai", "api_key": "sk-..." }
        """
        input_name = model_config.get("name", "").lower().strip()
        provider = model_config.get("provider", "openai").lower() 
        api_key = model_config.get("api_key")

        # STRICT DEMO MAPPING
        # Force specific versions for stability
        model_id = "gpt-4o" # Default fallback
        
        if "gpt" in input_name or "openai" in provider:
            model_id = "gpt-4o"
            provider = "openai"
        elif "claude" in input_name or "anthropic" in provider:
            model_id = "claude-3-haiku-20240307"
            provider = "anthropic"
        else:
            # Fallback or unknown
            if "claude" in input_name: 
                model_id = "claude-3-haiku-20240307"
                provider = "anthropic"

        if not api_key:
            raise ValueError(f"No API Key provided for model {model_id} ({provider})")

        start_time = time.time()
        output_text = ""
        
        # Prepare Prompt
        full_prompt = f"{prompt_template}\n\nTRANSCRIPT:\n{transcript}"

        try:
            if provider == "openai":
                client = openai.OpenAI(api_key=api_key)
                completion = client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "user", "content": full_prompt}]
                )
                output_text = completion.choices[0].message.content

            elif provider == "anthropic":
                # Standard SDK usage as requested - EXACT FIX
                from anthropic import Anthropic
                client = Anthropic(api_key=api_key)
                
                # Hardcoded demo-safe model
                model_id = "claude-3-haiku-20240307"

                message = client.messages.create(
                    model=model_id,
                    max_tokens=1024,
                    messages=[{
                        "role": "user", 
                        "content": [{"type": "text", "text": full_prompt}]
                    }]
                )
                output_text = message.content[0].text

            else:
                raise ValueError(f"Unsupported provider: {provider}")

        except Exception as e:
            # Re-raise to let Orchestrator handle it locally
            raise RuntimeError(f"Provider {provider} ({model_id}) failed: {str(e)}")

        latency = int((time.time() - start_time) * 1000)
        
        # Simple cost heuristic (placeholder)
        cost = 0.01 

        return {
            "raw_output": output_text,
            "latency_ms": latency,
            "cost_usd": cost,
            "model_name": model_id # Return actual used model ID
        }

    def evaluate_output(self, raw_output: str) -> Dict[str, Any]:
        """
        Heuristic evaluation of the output.
        """
        scores = []
        
        # 1. Edit Quality (Length check - assuming edits should be concise)
        length_score = 5
        if len(raw_output) < 50: length_score = 2
        elif len(raw_output) > 5000: length_score = 3
        scores.append({"metric_name": "edit_quality", "score": length_score, "reasoning": "Heuristic based on length"})

        # 2. Structural Clarity (JSON check or just structure)
        structure_score = 5 
        if "{" in raw_output and "}" in raw_output: structure_score = 5
        elif "\n" not in raw_output: structure_score = 3
        scores.append({"metric_name": "structural_clarity", "score": structure_score, "reasoning": "Heuristic based on formatting"})

        # 3. Publish Ready
        publish_score = 4
        scores.append({"metric_name": "publish_ready", "score": publish_score, "reasoning": "Heuristic default"})

        return {"scores": scores}

    def compare_models(self, runs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare runs and pick a winner.
        runs_data: list of dicts with {model_name, scores, cost, latency}
        """
        if not runs_data:
            return {"winning_model": "None", "reason": "No runs", "tradeoffs": {}}

        # Simple logic: pick highest total score
        best_run = None
        best_score = -1

        for run in runs_data:
            total = sum(s["score"] for s in run["scores"])
            if total > best_score:
                best_score = total
                best_run = run
        
        return {
            "winning_model": best_run["model_name"],
            "reason": "Highest heuristic quality score.",
            "tradeoffs": {"latency": f"{best_run['latency_ms']}ms"}
        }


class SupabaseClient:
    """Client for Supabase persistence."""

    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
        self.supabase: Client = create_client(url, key)

    def create_experiment(self, media_id: str) -> str:
        response = self.supabase.table("experiments").insert({"media_id": media_id, "status": "running"}).execute()
        if not response.data:
            raise Exception("Failed to create experiment")
        return response.data[0]["experiment_id"]

    def update_experiment_status(self, experiment_id: str, status: ExperimentStatus, error: Optional[str] = None):
        data = {"status": status.value}
        if error:
            data["error_log"] = error
        
        print(f"[Supabase] Updating {experiment_id} -> {status}. Payload: {data}")
        self.supabase.table("experiments").update(data).eq("experiment_id", experiment_id).execute()

    def insert_model_run(self, result: ModelRunResult):
        data = result.model_dump(mode='json')
        self.supabase.table("model_runs").insert(data).execute()

    def insert_eval_metrics(self, result: EvaluationResult):
        data = result.model_dump(mode='json')
        self.supabase.table("eval_metrics").insert(data).execute()

    def update_experiment_recommendation(self, result: ComparisonResult):
        data = {
            "recommendation": result.winning_model,
            "recommendation_reason": result.reason,
            "tradeoffs": result.tradeoffs
        }
        self.supabase.table("experiments").update(data).eq("experiment_id", result.experiment_id).execute()

    def update_experiment_decision(self, experiment_id: str, decision: Decision, decision_reason: str):
        data = {
            "decision": decision.value,
            "decision_reason": decision_reason
        }
        self.supabase.table("experiments").update(data).eq("experiment_id", experiment_id).execute()

    def get_experiments(self, limit: int = 50) -> List[Dict[str, Any]]:
        response = self.supabase.table("experiments").select("*").order("created_at", desc=True).limit(limit).execute()
        return response.data if response.data else []

    def get_experiment_details(self, experiment_id: str) -> Dict[str, Any]:
        # Fetch experiment
        exp_res = self.supabase.table("experiments").select("*").eq("experiment_id", experiment_id).execute()
        if not exp_res.data:
            return None
        
        experiment = exp_res.data[0]
        
        # Fetch runs
        runs_res = self.supabase.table("model_runs").select("*").eq("experiment_id", experiment_id).execute()
        runs = runs_res.data if runs_res.data else []
        
        # Enrich runs with metrics
        enriched_runs = []
        for run in runs:
            metrics_res = self.supabase.table("eval_metrics").select("*").eq("run_id", run["run_id"]).execute()
            metrics = metrics_res.data[0] if metrics_res.data else None
            
            run_data = {
                **run,
                "metrics": metrics
            }
            enriched_runs.append(run_data)
        
        return {
            "experiment": experiment,
            "runs": enriched_runs
        }
