from typing import Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseToolImpl


class SpotifyArgsSchema(BaseModel):
    query: str = Field(..., description="Track or playlist query to search/play")


class SpotifyPlayTool(BaseToolImpl):
    """Tool to control Spotify music playback."""

    name: str = "spotify.play"
    description: str = "Play a track or playlist on Spotify."
    args_model: type[BaseModel] = SpotifyArgsSchema
    requires_permission: bool = True

    async def _run(self, arguments: Dict[str, Any]) -> Any:
        return {"status": "playing", "query": arguments["query"]}
