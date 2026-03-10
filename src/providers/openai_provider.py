import time
import openai
from .base import ProviderInterface, ProviderResult

class OpenAIProvider(ProviderInterface):
    """OpenAI API implementation."""
    
    def generate(self, prompt: str, api_key: str, model: str) -> ProviderResult:
        if not api_key:
            raise ValueError(f"No API Key provided for OpenAI model {model}")
            
        client = openai.OpenAI(api_key=api_key)
        
        start_time = time.time()
        
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2  # Match context parking style (deterministic)
            )
            output_text = completion.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Provider openai ({model}) failed: {str(e)}")
            
        latency = int((time.time() - start_time) * 1000)
        
        # Simple cost heuristic (placeholder for now, could be updated with token counting)
        cost = 0.01 
        
        return ProviderResult(
            raw_output=output_text,
            latency_ms=latency,
            cost_usd=cost,
            model_name=model
        )
