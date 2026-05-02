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


def test_notification_sanitizes_contradictory_llm_send_copy() -> None:
    """LLM sometimes emits 'failed to send' while the mock tool still reports sent."""
    state: dict = {
        "appointment": {
            "appointment_id": "APP-X",
            "user_name": "Pat",
            "user_contact": "+1999",
            "doctor": "D1",
            "specialization": "Cardiology",
            "time_iso": "2026-05-02T10:00:00",
            "channel": "sms",
        },
        "status": "complete",
        "errors": [],
    }
    fake_llm = {
        "message": {
            "content": '{"notification": {"message": "Failed to send notification."}}',
        }
    }
    with patch("agents.notification_agent.ollama.chat", return_value=fake_llm), patch(
        "agents.notification_agent.save_appointment",
        return_value=True,
    ):
        res = notification_agent(state)

    assert res["notification"]["status"] == "sent"
    assert "Failed to send" not in (res["notification"].get("message") or "")
    assert "APP-X" in (res["notification"].get("message") or "")


def test_notification_sanitizes_pydantic_style_llm_copy() -> None:
    state: dict = {
        "appointment": {
            "appointment_id": "APP-Z",
            "user_name": "Pat",
            "user_contact": "+1999",
            "doctor": "D1",
            "specialization": "Cardiology",
            "time_iso": "2026-05-02T10:00:00",
            "channel": "sms",
        },
        "status": "complete",
        "errors": [],
    }
    fake_llm = {
        "message": {
            "content": '{"notification": {"message": "Missing required field \'user_contact\'"}}',
        }
    }
    with patch("agents.notification_agent.ollama.chat", return_value=fake_llm), patch(
        "agents.notification_agent.save_appointment",
        return_value=True,
    ):
        res = notification_agent(state)

    assert res["notification"]["status"] == "sent"
    assert "Missing required field" not in (res["notification"].get("message") or "")
    assert "APP-Z" in (res["notification"].get("message") or "")
