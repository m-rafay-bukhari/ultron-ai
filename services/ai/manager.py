import logging
from typing import Dict, Any, Optional, List, AsyncIterator
from services.ai.provider import BaseModelProvider, ModelStatus
from services.ai.models import ModelConfig, ModelMetadata
from services.ai.exceptions import (
    ModelNotFoundError,
    ModelLoadError,
    ModelExecutionError,
    DuplicateModelError,
    InvalidModelConfigError,
)
from services.ai.registry import ModelRegistry

logger = logging.getLogger(__name__)


class ModelManager:
    """The central orchestration gateway managing LLM configurations and provider lifecycles."""

    def __init__(self, registry: Optional[ModelRegistry] = None) -> None:
        self.registry = registry or ModelRegistry()
        self._models: Dict[str, BaseModelProvider] = {}
        self._configs: Dict[str, tuple[ModelConfig, ModelMetadata]] = {}

    def register_model(
        self, model_id: str, config: ModelConfig, metadata: ModelMetadata
    ) -> None:
        """Register a model instance configuration under a unique ID."""
        model_id_clean = model_id.strip()
        if not model_id_clean:
            raise InvalidModelConfigError("Model ID cannot be empty.")
        if model_id_clean in self._configs:
            raise DuplicateModelError(f"Model ID '{model_id}' is already registered.")

        if not config.provider or not config.provider.strip():
            raise InvalidModelConfigError("Model config must specify a provider.")
        if not config.model_name or not config.model_name.strip():
            raise InvalidModelConfigError("Model config must specify a model_name.")

        self._configs[model_id_clean] = (config, metadata)
        logger.info(
            f"Model config registered: {model_id_clean} (provider={config.provider})"
        )

    async def load_model(self, model_id: str) -> None:
        """Load and initialize a registered model's execution instance."""
        model_id_clean = model_id.strip()
        if model_id_clean not in self._configs:
            raise ModelNotFoundError(f"Model '{model_id}' is not registered.")

        # If model is already loaded and ready, skip initialization
        if model_id_clean in self._models:
            active_model = self._models[model_id_clean]
            if active_model.status == ModelStatus.READY:
                return

        config, metadata = self._configs[model_id_clean]
        provider_cls = self.registry.get_provider_class(config.provider)

        model_instance = provider_cls(config, metadata)
        self._models[model_id_clean] = model_instance
        model_instance.status = ModelStatus.LOADING

        try:
            logger.info(f"Loading provider instance for model '{model_id_clean}'")
            await model_instance.load()
            model_instance.status = ModelStatus.READY
            logger.info(f"Model '{model_id_clean}' is ready for execution.")
        except Exception as e:
            model_instance.status = ModelStatus.FAILED
            logger.error(f"Failed to load model '{model_id_clean}': {e}", exc_info=True)
            raise ModelLoadError(
                f"Failed to load model '{model_id_clean}': {str(e)}"
            ) from e

    async def unload_model(self, model_id: str) -> None:
        """Unload and clean up execution resources of a model instance."""
        model_id_clean = model_id.strip()
        if model_id_clean not in self._models:
            logger.debug(f"Model '{model_id_clean}' is not active.")
            return

        model_instance = self._models[model_id_clean]
        try:
            logger.info(f"Unloading model '{model_id_clean}'")
            await model_instance.unload()
            model_instance.status = ModelStatus.UNLOADED
            del self._models[model_id_clean]
            logger.info(f"Model '{model_id_clean}' successfully unloaded.")
        except Exception as e:
            logger.error(
                f"Failed to unload model '{model_id_clean}': {e}", exc_info=True
            )
            raise ModelLoadError(
                f"Failed to unload model '{model_id_clean}': {str(e)}"
            ) from e

    async def get_model(self, model_id: str) -> BaseModelProvider:
        """Retrieve an active model instance, loading it on-demand if necessary."""
        model_id_clean = model_id.strip()
        if model_id_clean not in self._configs:
            raise ModelNotFoundError(f"Model '{model_id}' is not registered.")

        if (
            model_id_clean not in self._models
            or self._models[model_id_clean].status != ModelStatus.READY
        ):
            await self.load_model(model_id_clean)

        return self._models[model_id_clean]

    async def generate(
        self, model_id: str, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute a text completion generation on the target model."""
        model = await self.get_model(model_id)
        try:
            return await model.generate(prompt, options)
        except Exception as e:
            logger.error(f"Execution failed on model '{model_id}': {e}", exc_info=True)
            raise ModelExecutionError(
                f"Execution failed on model '{model_id}': {str(e)}"
            ) from e

    async def generate_stream(
        self, model_id: str, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """Execute a token-streaming completion query on the target model."""
        model = await self.get_model(model_id)
        try:
            async for chunk in model.generate_stream(prompt, options):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming failed on model '{model_id}': {e}", exc_info=True)
            raise ModelExecutionError(
                f"Streaming failed on model '{model_id}': {str(e)}"
            ) from e

    async def check_model_health(self, model_id: str) -> bool:
        """Query and evaluate the health state of the model provider."""
        model_id_clean = model_id.strip()
        if model_id_clean not in self._configs:
            raise ModelNotFoundError(f"Model '{model_id}' is not registered.")

        # Resolve or instantiate instance
        if model_id_clean not in self._models:
            config, metadata = self._configs[model_id_clean]
            provider_cls = self.registry.get_provider_class(config.provider)
            self._models[model_id_clean] = provider_cls(config, metadata)

        model_instance = self._models[model_id_clean]
        try:
            return await model_instance.check_health()
        except Exception as e:
            logger.error(
                f"Health check diagnostics failed on model '{model_id_clean}': {e}"
            )
            return False

    def list_active_models(self) -> List[str]:
        """Return a list of all loaded model IDs."""
        return [k for k, v in self._models.items() if v.status == ModelStatus.READY]

    def list_registered_models(self) -> List[str]:
        """Return a list of all registered model configurations."""
        return list(self._configs.keys())

    def get_model_status(self, model_id: str) -> ModelStatus:
        """Get the current state of a registered model ID."""
        model_id_clean = model_id.strip()
        if model_id_clean not in self._configs:
            raise ModelNotFoundError(f"Model '{model_id}' is not registered.")
        if model_id_clean not in self._models:
            return ModelStatus.UNLOADED
        return self._models[model_id_clean].status
