"""
Tests for configuration management.
"""

import pytest
import os
from src.config import Settings, validate_config


def test_settings_loading():
    """Test that settings can be loaded from environment."""
    # Test with minimal required settings
    os.environ.update({
        "FIREWORKS_API_KEY": "test_key",
        "FIREWORKS_MODEL_ID": "test_model",
        "SERPER_API_KEY": "test_serper",
        "JINA_AI_API_KEY": "test_jina"
    })
    
    settings = Settings()
    
    assert settings.fireworks_api_key == "test_key"
    assert settings.fireworks_model_id == "test_model"
    assert settings.serper_api_key == "test_serper"
    assert settings.jina_ai_api_key == "test_jina"
    assert settings.agent_name == "SentientEcho"  # Default value


def test_validation_success():
    """Test successful configuration validation."""
    os.environ.update({
        "FIREWORKS_API_KEY": "test_key",
        "FIREWORKS_MODEL_ID": "test_model", 
        "SERPER_API_KEY": "test_serper",
        "JINA_AI_API_KEY": "test_jina"
    })
    
    # Should not raise an exception
    assert validate_config() is True


def test_validation_failure():
    """Test configuration validation with missing keys."""
    # Clear required environment variables
    for key in ["FIREWORKS_API_KEY", "FIREWORKS_MODEL_ID", "SERPER_API_KEY", "JINA_AI_API_KEY"]:
        if key in os.environ:
            del os.environ[key]
    
    with pytest.raises(ValueError) as exc_info:
        validate_config()
    
    assert "Missing required environment variables" in str(exc_info.value)
