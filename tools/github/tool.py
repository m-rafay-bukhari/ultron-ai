from typing import Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseToolImpl

class GithubArgsSchema(BaseModel):
    repo: str = Field(..., description="Repository owner/name (e.g. 'octocat/Hello-World')")

class GithubRepoTool(BaseToolImpl):
    """Tool to fetch GitHub repository details."""
    name: str = "github.get_repo"
    description: str = "Retrieve details and metadata about a public GitHub repository."
    args_model: type[BaseModel] = GithubArgsSchema

    async def _run(self, arguments: Dict[str, Any]) -> Any:
        return {"repo": arguments["repo"], "stars": 42, "forks": 10}
