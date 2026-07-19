from typing import Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseToolImpl


class WeatherArgsSchema(BaseModel):
    location: str = Field(..., description="City and country name (e.g. 'London, UK')")


class GetWeatherTool(BaseToolImpl):
    """Tool to fetch weather information."""

    name: str = "weather.get_current"
    description: str = "Fetch current weather conditions for a location."
    args_model: type[BaseModel] = WeatherArgsSchema

    async def _run(self, arguments: Dict[str, Any]) -> Any:
        return {"location": arguments["location"], "temp_c": 21.0, "condition": "sunny"}
