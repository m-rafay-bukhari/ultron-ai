from typing import Dict, Any, Optional, AsyncIterator
from services.ai import (
    BaseModelProvider,
    ProviderCapability,
)


class SecondProvider(BaseModelProvider):
    provider_name = "second"
    capabilities = [ProviderCapability.EMBEDDINGS, ProviderCapability.VISION]

    async def load(self) -> None:
        pass

    async def unload(self) -> None:
        pass

    async def check_health(self) -> bool:
        return True

    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> str:
        return ""

    async def generate_stream(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        yield ""
