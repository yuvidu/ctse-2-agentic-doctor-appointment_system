from __future__ import annotations

from unittest.mock import patch

from agents.notification_agent import notification_agent


def test_notification_agent_integration_preserves_top_level_status() -> None:
    state: dict = {
        "appointment": {
            "appointment_id": "TINT1",
            "user_name": "Test",
            "user_contact": "+1111",
            "doctor": "TestDr",
            "specialization": "General Medicine",
            "time_iso": "2026-05-06T09:00:00",
            "channel": "sms",
        },
        "status": "complete",
        "errors": [],
    }

    fake_llm = {
        "message": {
            "content": '{"notification": {"message": "Hello from test"}}',
        }
    }

    with patch("agents.notification_agent.ollama.chat", return_value=fake_llm), patch(
        "agents.notification_agent.save_appointment",
        return_value=True,
    ):
        res = notification_agent(state)

    assert "notification" in res
    assert res["notification"]["status"] == "sent"
    assert res["status"] == "complete"
