import sys
import os

# Make repo importable when tests run
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.notification_agent import notification_agent


def test_notification_agent_integration():
    state = {
        "appointment": {
            "appointment_id": "TINT1",
            "user_name": "Test",
            "user_contact": "+1111",
            "doctor": "TestDr",
            "specialization": "General",
            "time_iso": "2026-05-06T09:00:00",
            "channel": "sms",
        },
        "status": "pending",
        "errors": [],
    }

    res = notification_agent(state)

    assert "notification" in res
    assert res["notification"]["status"] == "sent"
    assert res["status"] == "confirmed"


if __name__ == "__main__":
    test_notification_agent_integration()
    print("integration test: OK")
