import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Dispatches system-level popups, native toasts, and notification alerts."""

    def __init__(self) -> None:
        pass

    async def send_desktop_notification(self, title: str, message: str) -> bool:
        logger.info(f"Posting desktop alert: [{title}] {message}")
        return True
