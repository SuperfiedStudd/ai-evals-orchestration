from typing import Dict, Any, Optional
from pydantic import BaseModel

class ProviderResult(BaseModel):
    """Standardized output from any AI provider."""
    raw_output: str
    latency_ms: int
    cost_usd: float
    model_name: str

class ProviderInterface:
    """Unified interface for all AI model providers."""
    
    def generate(self, prompt: str, api_key: str, model: str) -> ProviderResult:
        """
        Executes a prompt against the provider's specific model.
        
        Args:
            prompt: The full formatted prompt (system + user transcript).
            api_key: The provider-specific API key.
            model: The specific model identifier (e.g. gpt-4o, claude-3-opus).
            
        Returns:
            ProviderResult containing the raw text, latency, and estimated cost.
            
        Raises:
            Exception: If provider API call fails. Should be caught by the orchestrator.
        """
        raise NotImplementedError("Providers must implement generate()")
