from typing import Any, List, Tuple
from tools.notification_tools.notification_tool import send_notification, Appointment

def test_send_notification_calls_logger_and_returns_sent():
    appt: Appointment = {
        "appointment_id": "B456",
        "user_name": "Bob",
        "user_contact": "+1987654321",
        "doctor": "Jones",
        "specialization": "Cardiology",
        "time_iso": "2026-05-04T14:30:00",
        "channel": "email",
    }

    calls: List[Tuple[str, str, Any]] = []

    def stub_logger(agent: str, step: str, data: Any) -> None:
        calls.append((agent, step, data))

    result = send_notification(appt, message="Test Message", channel="email", logger=stub_logger)

    assert result["status"] == "sent"
    assert result["channel"] == "email"
    assert result["message"] == "Test Message"
    assert len(calls) >= 2


def test_send_notification_handles_logger_exception():
    appt: Appointment = {
        "appointment_id": "C789",
        "user_name": "Carol",
        "user_contact": "+1011121314",
        "doctor": "Lee",
        "specialization": "General",
        "time_iso": "2026-05-05T09:00:00",
        "channel": "sms",
    }

    def bad_logger(agent: str, step: str, data: Any) -> None:
        raise RuntimeError("logger failed")

    result = send_notification(appt, message="Test Message", channel="sms", logger=bad_logger)

    assert result["status"] == "failed"
    assert result["error"] is not None
