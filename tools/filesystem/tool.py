from typing import Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseToolImpl


class ReadFileSchema(BaseModel):
    path: str = Field(..., description="Absolute path of the file to read")


class ReadFileTool(BaseToolImpl):
    """Tool to read files from the local filesystem."""

    name: str = "filesystem.read_file"
    description: str = "Read the contents of a file on the disk."
    args_model: type[BaseModel] = ReadFileSchema
    requires_permission: bool = True

    async def _run(self, arguments: Dict[str, Any]) -> Any:
        # Skeletal execution - no actual reading
        return f"Skeletal content for path: {arguments['path']}"
