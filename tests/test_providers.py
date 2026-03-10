import pytest
from pydantic import ValidationError
# Imports structured exactly like test_orchestrator.py (from src.<module>)
from src.providers.registry import get_provider, resolve_model
from src.providers.gemini_provider import GeminiProvider
from src.providers.openai_provider import OpenAIProvider
from src.providers.anthropic_provider import AnthropicProvider

def test_registry_canonical_gemini():
    """Verify that 'gemini' resolves to the GeminiProvider explicitly."""
    provider = get_provider("gemini")
    assert isinstance(provider, GeminiProvider)
    
def test_registry_google_alias_resolves_to_gemini():
    """Verify that 'google' resolves backward-compatibly to the GeminiProvider."""
    provider = get_provider("google")
    assert isinstance(provider, GeminiProvider)

def test_registry_other_providers():
    """Verify standard providers resolve correctly."""
    assert isinstance(get_provider("openai"), OpenAIProvider)
    assert isinstance(get_provider("anthropic"), AnthropicProvider)

def test_registry_invalid_provider():
    """Verify registry raises error on unknown provider."""
    with pytest.raises(ValueError, match="Unsupported provider: 'unknown'"):
        get_provider("unknown")

def test_resolve_model_defaults():
    """Verify missing models resolve to provider defaults."""
    assert resolve_model("gemini", "") == "gemini-2.0-flash"
    assert resolve_model("google", "") == "gemini-2.0-flash" # Alias also gets correct default
    assert resolve_model("openai", None) == "gpt-4o"
    assert resolve_model("anthropic", "   ") == "claude-3-haiku-20240307"

def test_resolve_model_explicit():
    """Verify explicit models override defaults."""
    assert resolve_model("gemini", "gemini-pro") == "gemini-pro"
    assert resolve_model("openai", "gpt-3.5") == "gpt-3.5"
