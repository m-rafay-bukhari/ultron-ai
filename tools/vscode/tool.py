from typing import Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseToolImpl

class VSCodeArgsSchema(BaseModel):
    filepath: str = Field(..., description="The path of the file to open in VS Code")

class VSCodeOpenFileTool(BaseToolImpl):
    """Tool to open files inside VS Code workspace."""
    name: str = "vscode.open_file"
    description: str = "Open a file inside VS Code."
    args_model: type[BaseModel] = VSCodeArgsSchema
    requires_permission: bool = True

    async def _run(self, arguments: Dict[str, Any]) -> Any:
        return {"status": "opened", "filepath": arguments["filepath"]}
