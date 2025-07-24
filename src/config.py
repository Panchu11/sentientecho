"""Configuration management for SentientEcho agent."""

import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Fireworks AI Configuration
    fireworks_api_key: str = Field(..., env="FIREWORKS_API_KEY")
    fireworks_model_id: str = Field(..., env="FIREWORKS_MODEL_ID")
    
    # Search API Configuration
    serper_api_key: str = Field(..., env="SERPER_API_KEY")
    jina_ai_api_key: str = Field(..., env="JINA_AI_API_KEY")
    
    # Agent Configuration
    agent_name: str = Field(default="SentientEcho", env="AGENT_NAME")
    agent_port: int = Field(default=8000, env="AGENT_PORT")
    agent_host: str = Field(default="0.0.0.0", env="AGENT_HOST")
    
    # Search Configuration
    max_reddit_results: int = Field(default=10, env="MAX_REDDIT_RESULTS")
    max_twitter_results: int = Field(default=10, env="MAX_TWITTER_RESULTS")
    default_time_range_days: int = Field(default=7, env="DEFAULT_TIME_RANGE_DAYS")
    enable_summaries: bool = Field(default=True, env="ENABLE_SUMMARIES")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Optional Reddit API (backup)
    reddit_client_id: Optional[str] = Field(default=None, env="REDDIT_CLIENT_ID")
    reddit_client_secret: Optional[str] = Field(default=None, env="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(default="SentientEcho/1.0", env="REDDIT_USER_AGENT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


# Validation
def validate_config():
    """Validate that all required configuration is present."""
    required_fields = [
        "fireworks_api_key",
        "fireworks_model_id", 
        "serper_api_key",
        "jina_ai_api_key"
    ]
    
    missing_fields = []
    for field in required_fields:
        if not getattr(settings, field):
            missing_fields.append(field.upper())
    
    if missing_fields:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_fields)}")
    
    return True


if __name__ == "__main__":
    # Test configuration loading
    try:
        validate_config()
        print("✅ Configuration loaded successfully!")
        print(f"Agent: {settings.agent_name}")
        print(f"Port: {settings.agent_port}")
        print(f"Model: {settings.fireworks_model_id}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
