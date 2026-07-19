import json
import logging
import os
from typing import Dict, Any, Optional, List, Callable
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from services.ai.models import ModelConfig

logger = logging.getLogger(__name__)


class ProviderConfig(BaseSettings):
    """Base settings model for all AI providers."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    timeout: float = Field(
        default=30.0, description="Network timeout threshold in seconds"
    )
    additional_params: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary provider-specific parameters"
    )


class OllamaProviderConfig(ProviderConfig):
    """Configuration settings specific to Ollama local instances."""

    api_base: str = Field(
        default="http://localhost:11434",
        description="Target endpoint URL for local Ollama APIs",
    )


class OpenAIProviderConfig(ProviderConfig):
    """Configuration settings specific to OpenAI remote endpoints."""

    api_key: Optional[str] = Field(
        default=None, description="API credential key for OpenAI"
    )
    api_base: Optional[str] = Field(
        default=None, description="Optional custom base endpoint URL"
    )
    organization: Optional[str] = Field(
        default=None, description="Optional organization identifier"
    )


class AnthropicProviderConfig(ProviderConfig):
    """Configuration settings specific to Anthropic remote endpoints."""

    api_key: Optional[str] = Field(
        default=None, description="API credential key for Anthropic Claude"
    )
    api_base: Optional[str] = Field(
        default=None, description="Optional custom base endpoint URL"
    )


class GeminiProviderConfig(ProviderConfig):
    """Configuration settings specific to Google Gemini APIs."""

    api_key: Optional[str] = Field(
        default=None, description="API credential key for Gemini services"
    )


class AIConfig(BaseSettings):
    """Centralized configuration schema managing all provider settings and model definitions."""

    model_config = SettingsConfigDict(
        env_prefix="ULTRON_AI_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    default_model: str = Field(
        default="ollama-llama3",
        description="Global fallback model ID for reasoning tasks",
    )

    # Provider configurations
    ollama: OllamaProviderConfig = Field(default_factory=OllamaProviderConfig)
    openai: OpenAIProviderConfig = Field(default_factory=OpenAIProviderConfig)
    anthropic: AnthropicProviderConfig = Field(default_factory=AnthropicProviderConfig)
    gemini: GeminiProviderConfig = Field(default_factory=GeminiProviderConfig)

    # Pre-configured model mappings: model_id -> ModelConfig
    models: Dict[str, ModelConfig] = Field(
        default_factory=dict, description="Predefined list of registered active models"
    )


class ModelConfigLoader:
    """Central loader responsible for managing configuration files, environmental overrides, and hot-reload callbacks."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        self.config_path = config_path
        self._config: AIConfig = AIConfig()
        self._on_reload_callbacks: List[Callable[[AIConfig], None]] = []
        self.load()

    def load(self) -> None:
        """Load and validate settings from config path and environment overrides."""
        logger.info("Initializing AI Configuration loading...")
        file_settings: Dict[str, Any] = {}

        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    file_settings = json.load(f)
                logger.info(f"Loaded config file parameters from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to parse config file '{self.config_path}': {e}")
                # Graceful fallback to default/env values

        try:
            # Construct configuration. Environmental variables override file values.
            self._config = AIConfig(**file_settings)
            logger.info("AI Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"AI Configuration validation failed: {e}")
            raise

    def get_config(self) -> AIConfig:
        """Retrieve the current validated AIConfig settings."""
        return self._config

    def register_on_reload(self, callback: Callable[[AIConfig], None]) -> None:
        """Register a callback function to execute when configurations are hot-reloaded."""
        self._on_reload_callbacks.append(callback)

    def reload(self) -> None:
        """Reload configuration from disk/environment and trigger all registered callbacks."""
        logger.info("Hot-reloading AI Configuration...")
        self.load()
        for callback in self._on_reload_callbacks:
            try:
                callback(self._config)
            except Exception as e:
                logger.error(
                    f"Error executing config reload callback: {e}", exc_info=True
                )
