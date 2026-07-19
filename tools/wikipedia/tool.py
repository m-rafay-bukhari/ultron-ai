from typing import Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseToolImpl


class WikipediaArgsSchema(BaseModel):
    query: str = Field(..., description="The search query to lookup on Wikipedia")


class WikipediaSearchTool(BaseToolImpl):
    """Tool to search Wikipedia articles."""

    name: str = "wikipedia.search"
    description: str = "Search for a query on Wikipedia and retrieve summaries."
    args_model: type[BaseModel] = WikipediaArgsSchema

    async def _run(self, arguments: Dict[str, Any]) -> Any:
        return {
            "query": arguments["query"],
            "summary": f"Skeletal Wikipedia summary for '{arguments['query']}'",
        }
