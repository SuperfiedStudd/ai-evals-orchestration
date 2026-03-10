import time
from .base import ProviderInterface, ProviderResult

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

class GeminiProvider(ProviderInterface):
    """Google Gemini API implementation."""
    
    def generate(self, prompt: str, api_key: str, model: str) -> ProviderResult:
        if not genai:
            raise RuntimeError("google-genai package is not installed.")
        if not api_key:
            raise ValueError(f"No API Key provided for Gemini model {model}")
            
        client = genai.Client(api_key=api_key)
        
        start_time = time.time()
        
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                )
            )
            output_text = response.text
        except Exception as e:
            raise RuntimeError(f"Provider gemini ({model}) failed: {str(e)}")
            
        latency = int((time.time() - start_time) * 1000)
        
        cost = 0.01 
        
        return ProviderResult(
            raw_output=output_text,
            latency_ms=latency,
            cost_usd=cost,
            model_name=model
        )
