import sys
import logging
from src.models import ExperimentInput, MediaType, Decision
from src.orchestrator import OrchestrationEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing Orchestration Engine...")
    engine = OrchestrationEngine()
    
    # 1. Setup Input Data
    input_data = ExperimentInput(
        media_id="demo_audio_clip_001",
        media_type=MediaType.AUDIO,
        model_list=["gpt-4o", "claude-3-opus"],
        user_api_keys={"gpt-4o": "sk-mock", "claude-3-opus": "sk-mock"},
        experiment_metadata={"project": "creative-demo"}
    )
    
    # 2. Create Experiment
    logger.info("Creating Experiment...")
    experiment_id = engine.create_experiment(input_data.media_id)
    logger.info(f"Experiment Created: {experiment_id}")
    
    # 3. Run Flow (Run Models -> Evaluate -> Compare)
    logger.info("Starting Execution Loop...")
    try:
        engine.run_experiment_flow(experiment_id, input_data)
        logger.info("Execution Loop Complete. Models run, evaluated, and compared.")
    except Exception as e:
        logger.error(f"Experiment Failed: {e}")
        return

    # 4. Simulate Human Decision
    logger.info("Waiting for Human Decision... (Simulating 'SHIP')")
    decision_reason = "GPT-4o had better structure and lower latency."
    engine.submit_human_decision(experiment_id, Decision.SHIP, decision_reason)
    
    logger.info(f"Experiment {experiment_id} marked as COMPLETE with decision SHIP.")

if __name__ == "__main__":
    main()
