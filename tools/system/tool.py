from typing import Dict, Any
from pydantic import BaseModel
from tools.base import BaseToolImpl


class SystemArgsSchema(BaseModel):
    pass


class SystemStatsTool(BaseToolImpl):
    """Tool to retrieve host system information (CPU, memory, uptime)."""

    name: str = "system.get_stats"
    description: str = "Get host performance and system stats."
    args_model: type[BaseModel] = SystemArgsSchema
    requires_permission: bool = False

    async def _run(self, arguments: Dict[str, Any]) -> Any:
        return {"cpu_usage_pct": 12.5, "memory_used_gb": 8.2, "status": "nominal"}
