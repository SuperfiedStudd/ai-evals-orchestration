import time
from anthropic import Anthropic
from .base import ProviderInterface, ProviderResult

class AnthropicProvider(ProviderInterface):
    """Anthropic API implementation."""
    
    def generate(self, prompt: str, api_key: str, model: str) -> ProviderResult:
        if not api_key:
            raise ValueError(f"No API Key provided for Anthropic model {model}")
            
        client = Anthropic(api_key=api_key)
        
        start_time = time.time()
        
        try:
            message = client.messages.create(
                model=model,
                max_tokens=4096,
                temperature=0.2,
                messages=[{
                    "role": "user", 
                    "content": [{"type": "text", "text": prompt}]
                }]
            )
            output_text = message.content[0].text
        except Exception as e:
            raise RuntimeError(f"Provider anthropic ({model}) failed: {str(e)}")
            
        latency = int((time.time() - start_time) * 1000)
        
        # Simple cost heuristic (placeholder)
        cost = 0.01 
        
        return ProviderResult(
            raw_output=output_text,
            latency_ms=latency,
            cost_usd=cost,
            model_name=model
        )
