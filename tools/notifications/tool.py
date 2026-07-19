from typing import Dict, Any
from pydantic import BaseModel, Field
from tools.base import BaseToolImpl


class NotificationArgsSchema(BaseModel):
    title: str = Field(..., description="The title of the notification alert")
    message: str = Field(..., description="The main content text of the notification")


class SendNotificationTool(BaseToolImpl):
    """Tool to post system/desktop notifications."""

    name: str = "notifications.send"
    description: str = "Send a desktop or UI notification alert."
    args_model: type[BaseModel] = NotificationArgsSchema

    async def _run(self, arguments: Dict[str, Any]) -> Any:
        return {"status": "sent", "title": arguments["title"]}
