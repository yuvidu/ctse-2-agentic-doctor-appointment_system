from typing import TypedDict, Callable, Any, Optional
from tools.notification_tools.logging_tool import log_event


class Appointment(TypedDict):
    """TypedDict describing an appointment record passed between agents."""

    appointment_id: str
    user_name: str
    user_contact: str
    doctor: str
    specialization: str
    time_iso: str
    channel: str


class NotificationResult(TypedDict):
    """TypedDict describing the result of a notification attempt."""

    status: str  # 'sent' or 'failed'
    channel: str
    message: str
    error: Optional[str]


LoggerType = Callable[[str, str, Any], None]


def send_notification(
    appointment: Appointment,
    message: str,
    channel: str = "sms",
    logger: LoggerType = log_event,
) -> NotificationResult:
    """Mock-sends a notification and logs the attempt.

    This function is intentionally deterministic and side-effect light: it does not
    call external services. Instead it logs the send attempt and returns a
    `NotificationResult` dict. The `logger` parameter is injectable to simplify
    unit testing.

    Args:
        appointment: The appointment data related to the message.
        message: The actual message to send.
        channel: The notification channel (e.g., 'sms' or 'email').
        logger: A callable used to persist/log events. Defaults to the project's
            `tools.notification_tools.logging_tool.log_event`.

    Returns:
        NotificationResult with status, channel, message and optional error.
    """

    try:
        logger("NotificationAgent", "send_attempt", {"appointment_id": appointment["appointment_id"], "channel": channel})

        # Simulate a successful send
        result: NotificationResult = {
            "status": "sent",
            "channel": channel,
            "message": message,
            "error": None,
        }

        logger("NotificationAgent", "send_result", result)
        return result

    except Exception as exc:  # pragma: no cover - defensive
        err = str(exc)
        result: NotificationResult = {"status": "failed", "channel": channel, "message": message, "error": err}
        try:
            logger("NotificationAgent", "send_error", {"error": err})
        except Exception:
            pass
        return result
