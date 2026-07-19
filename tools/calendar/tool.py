from typing import Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseToolImpl


class CalendarArgsSchema(BaseModel):
    summary: str = Field(..., description="Event summary/title")
    start_time: str = Field(
        ..., description="ISO 8601 start time (e.g. '2026-07-16T10:00:00')"
    )


class CalendarCreateEventTool(BaseToolImpl):
    """Tool to create calendar events."""

    name: str = "calendar.create_event"
    description: str = "Create a new event in the user's calendar."
    args_model: type[BaseModel] = CalendarArgsSchema
    requires_permission: bool = True

    async def _run(self, arguments: Dict[str, Any]) -> Any:
        return {
            "status": "created",
            "event_id": "cal-999",
            "summary": arguments["summary"],
        }
