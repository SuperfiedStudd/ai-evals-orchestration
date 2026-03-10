from typing import Dict, Type
from .base import ProviderInterface
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider

# Canonical provider names mapped to their implementation classes
PROVIDER_CLASS_MAP: Dict[str, Type[ProviderInterface]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
}

# Backward-compatible aliases (resolved before lookup)
PROVIDER_ALIASES: Dict[str, str] = {
    "google": "gemini",
}

# Canonical default models per provider
DEFAULT_MODELS: Dict[str, str] = {
    "openai": "gpt-4o",
    "anthropic": "claude-3-haiku-20240307",
    "gemini": "gemini-2.0-flash",
}

def _normalize_provider(name: str) -> str:
    """Normalize and resolve aliases to canonical provider name."""
    normalized = name.lower().strip()
    return PROVIDER_ALIASES.get(normalized, normalized)

def get_provider(provider_name: str) -> ProviderInterface:
    """
    Returns an instance of the requested provider.
    Accepts canonical names and backward-compatible aliases.
    Raises ValueError if the provider is unknown.
    """
    canonical = _normalize_provider(provider_name)
    
    if canonical not in PROVIDER_CLASS_MAP:
        raise ValueError(
            f"Unsupported provider: '{provider_name}'. "
            f"Valid providers: {list(PROVIDER_CLASS_MAP.keys())}"
        )
        
    return PROVIDER_CLASS_MAP[canonical]()

def resolve_model(provider_name: str, requested_model: str = "") -> str:
    """
    Returns the explicitly requested model if provided, 
    otherwise falls back to the provider's default model.
    """
    canonical = _normalize_provider(provider_name)
    
    if requested_model and requested_model.strip():
        return requested_model.strip()
        
    if canonical in DEFAULT_MODELS:
        return DEFAULT_MODELS[canonical]
        
    return "unknown-model"
