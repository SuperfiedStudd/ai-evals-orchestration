import json
import uuid
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

# FORCE FIX: Unset proxies to prevent Anthropic SDK crash
for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"]:
    if key in os.environ:
        del os.environ[key]

from .models import ExperimentInput, Decision, ExperimentStatus
from .orchestrator import OrchestrationEngine
from .services import AIProviderService, SupabaseClient

app = FastAPI()

# CORS for local UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
ai_service = AIProviderService()
supabase_client = SupabaseClient()
orchestrator = OrchestrationEngine(ai_service, supabase_client)

# --- Routes ---

@app.post("/v1/transcribe")
async def transcribe(file: UploadFile = File(None), text: str = Form(None)):
    """
    Transcribes audio file to text using OpenAI Whisper.
    If text is provided, returns it directly.
    """
    if text:
        return {
            "transcript": text,
            "provider": "manual_text",
            "latency_ms": 0,
            "cost_usd": 0.0
        }
    
    if file:
        # Save temp file
        temp_filename = f"temp_{uuid.uuid4()}_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            result = ai_service.transcribe_audio(temp_filename)
            # Cleanup
            import os
            os.remove(temp_filename)
            return {
                "transcript": result["transcript"],
                "provider": "openai-whisper",
                "latency_ms": result["latency_ms"],
                "cost_usd": result["cost_usd"]
            }
        except Exception as e:
            import os
            if os.path.exists(temp_filename): os.remove(temp_filename)
            raise HTTPException(status_code=500, detail=str(e))

    raise HTTPException(status_code=400, detail="Either file or text is required")

@app.post("/v1/experiment")
async def create_experiment(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(None), 
    text: str = Form(None), 
    models: str = Form(...) # JSON string
):
    """
    Starts an experiment.
    1. Creates experiment record.
    2. Runs orchestration in background.
    """
    try:
        model_list_data = json.loads(models)
        # model_list_data expects list of {name, provider, api_key}
        
        # Convert to ExperimentInput format expected by Orchestrator
        # Orchestrator expects: model_list (names), user_api_keys (name->key)
        # But we refactored logic, Orchestrator now takes... wait.
        # Orchestrator.run_experiment_flow logic:
        # It iterates input_data.model_list
        # It gets api_key from input_data.user_api_keys
        # It infers provider from name.
        
        # We need to map the incoming detailed models list to what Orchestrator expects
        # OR update Orchestrator to take full config objects. 
        # For minimal friction, let's map it here.
        
        names_list = [m["name"] for m in model_list_data]
        keys_map = {m["name"]: m["apiKey"] for m in model_list_data} 
        # Note: UI sends 'apiKey', adjust if needed. Code used 'api_key' in py models.
        
        experiment_input = ExperimentInput(
            media_id="upload", # Placeholder, updated in create_experiment
            media_type="audio" if file else "text",
            model_list=names_list,
            user_api_keys=keys_map
        )

        # 1. Create Experiment
        media_name = file.filename if file else "manual_text"
        experiment_id = orchestrator.create_experiment(media_name)

        # 2. Save file if needed for background task
        temp_file_path = None
        text_input = text
        
        if file:
            temp_file_path = f"temp_{uuid.uuid4()}_{file.filename}"
            with open(temp_file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        
        # 3. Schedule Background Task
        background_tasks.add_task(
            run_background_orchestration, 
            experiment_id, 
            experiment_input, 
            temp_file_path, 
            text_input
        )

        return {"experiment_id": experiment_id, "status": "running"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_background_orchestration(experiment_id: str, input_data: ExperimentInput, file_path: str, text_input: str):
    try:
        orchestrator.run_experiment_flow(experiment_id, input_data, file_path, text_input)
    finally:
        # Cleanup temp file
        if file_path:
            import os
            if os.path.exists(file_path):
                os.remove(file_path)

@app.get("/v1/experiment/{experiment_id}")
async def get_experiment(experiment_id: str):
    """
    Polls experiment status and results.
    """
    try:
        # Query Supabase directly for status
        exp_res = supabase_client.supabase.table("experiments").select("*").eq("experiment_id", experiment_id).execute()
        if not exp_res.data:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        experiment = exp_res.data[0]
        
        # Get Runs & Results if ready
        # We can implement a JOIN or just separate queries. 
        # For simplicity, separate queries.
        runs_res = supabase_client.supabase.table("model_runs").select("*").eq("experiment_id", experiment_id).execute()
        runs = runs_res.data
        
        # Get Metrics
        # This might be heavy if many runs, but we have max 3.
        # We need to join metrics to runs.
        # Let's just return the raw runs and let UI fetch more or include it here.
        # Better: UI expects a consolidated result object? 
        # The prompt says "results table once runs exist".
        # We should enrich the runs with metrics.
        
        enriched_results = []
        for run in runs:
            metrics_res = supabase_client.supabase.table("eval_metrics").select("*").eq("run_id", run["run_id"]).execute()
            scores = metrics_res.data[0]["scores"] if metrics_res.data else []
            
            # Simple aggregation for UI
            # We assume the UI wants specific fields.
            # Map valid heuristics to UI columns
            enriched_results.append({
                "model": run["model_name"],
                "cost": f"${run.get('cost_usd', 0):.4f}",
                "latency": f"{run.get('latency_ms', 0)}ms",
                "scores": scores
                # Add heuristic mapping if needed
            })
            
        return {
            "status": experiment["status"],
            "recommendation": experiment.get("recommendation"),
            "results": enriched_results,
            "error_log": experiment.get("error_log")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/experiments")
async def list_experiments(limit: int = 50):
    """
    List recent experiments.
    """
    try:
        return supabase_client.get_experiments(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/experiments/{experiment_id}/details")
async def get_experiment_details(experiment_id: str):
    """
    Get full details for an experiment.
    """
    try:
        details = supabase_client.get_experiment_details(experiment_id)
        if not details:
            raise HTTPException(status_code=404, detail="Experiment not found")
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/decision")
async def submit_decision(data: dict):
    """
    Submits human decision.
    """
    try:
        exp_id = data.get("experiment_id")
        decision_str = data.get("decision", "").lower() # Normalize to lowercase for Enum
        reason = data.get("decision_reason")
        
        orchestrator.submit_human_decision(
            exp_id, 
            Decision(decision_str), 
            reason
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
