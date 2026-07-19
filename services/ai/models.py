from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ModelMetadata(BaseModel):
    """Metadata describing a model's static capabilities and parameters."""

    context_window: int = Field(
        default=2048, description="Maximum token context length supported by the model"
    )
    capabilities: List[str] = Field(
        default_factory=list,
        description="List of model capabilities (e.g. text, vision, embedding)",
    )
    description: Optional[str] = Field(
        default=None, description="Optional description details for this model instance"
    )


class ModelConfig(BaseModel):
    """Configuration settings for connecting and executing a model instance."""

    provider: str = Field(
        ..., description="Name of the model provider (e.g. ollama, openai, gemini)"
    )
    model_name: str = Field(
        ..., description="Specific backend model identifier (e.g. llama3, gpt-4)"
    )
    api_key: Optional[str] = Field(
        default=None, description="API credential token for authentication"
    )
    api_base: Optional[str] = Field(
        default=None, description="Base endpoint target URL for queries"
    )
    temperature: float = Field(
        default=0.7, description="Sampling temperature parameter"
    )
    max_tokens: Optional[int] = Field(
        default=None, description="Maximum completion tokens limit"
    )
    timeout: float = Field(
        default=30.0, description="Network timeout threshold in seconds"
    )
    additional_params: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary provider-specific configurations"
    )
