from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, TypedDict

from utils.logging_utils import log_event as default_log_event


class NotificationResult(TypedDict):
    status: str
    channel: str
    message: str
    error: str | None


LoggerType = Callable[[str, str, Mapping[str, Any] | None], None]


def send_notification(
    appointment: Mapping[str, Any],
    message: str,
    channel: str = "sms",
    logger: LoggerType | None = None,
) -> NotificationResult:
    """Mock-send a notification and log the attempt (injectable ``logger`` for tests)."""
    log = logger or default_log_event
    try:
        log(
            "NotificationTool",
            "send_attempt",
            {"appointment_id": appointment["appointment_id"], "channel": channel},
        )
        result: NotificationResult = {
            "status": "sent",
            "channel": channel,
            "message": message,
            "error": None,
        }
        log("NotificationTool", "send_result", dict(result))
        return result
    except Exception as exc:  # pragma: no cover - defensive
        err = str(exc)
        result = {"status": "failed", "channel": channel, "message": message, "error": err}
        try:
            log("NotificationTool", "send_error", {"error": err})
        except Exception:
            pass
        return result
