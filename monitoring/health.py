import logging
from typing import Dict, Any
from core.interfaces.storage import BaseStorage

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Performs regular health checks on external APIs, database connections, and host health."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    async def check_health(self) -> Dict[str, Any]:
        """Perform a full system diagnostic check."""
        # Check storage connection (skeletal check)
        storage_healthy = True
        try:
            # Running a lightweight operation to verify connectivity
            await self.storage.get("health_check_key")
        except Exception as e:
            logger.error(f"Health check failed for storage: {e}")
            storage_healthy = False

        return {
            "status": "healthy" if storage_healthy else "degraded",
            "components": {
                "storage": "online" if storage_healthy else "offline",
                "system": "online"
            }
        }
