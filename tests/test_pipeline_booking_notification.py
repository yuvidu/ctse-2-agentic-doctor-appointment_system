"""Pipeline: notification skipped when booking does not confirm."""

from __future__ import annotations

import pipeline as pl


def test_run_system_skips_notification_agent_when_booking_not_confirmed(monkeypatch) -> None:
    calls: list[int] = []

    def capture_notification(s: dict) -> dict:
        calls.append(1)
        return s

    def fake_intent(s: dict) -> dict:
        return {"status": "complete", "intent": {"specialization": "X", "date": "2026-01-01"}}

    def fake_avail(s: dict, **kwargs) -> dict:
        return {
            "status": "availability_ok",
            "availability": {
                "available_slots": [
                    {
                        "doctor_id": "D1",
                        "start": "2026-01-01T10:00:00",
                        "end": "2026-01-01T10:30:00",
                        "location": "L",
                        "specialty": "x",
                    }
                ]
            },
        }

    def fake_booking(s: dict) -> dict:
        out = dict(s)
        out["booking"] = {"status": "conflict_detected", "detail": "taken"}
        out.setdefault("errors", []).append(
            {
                "code": "BOOKING_COLLISION",
                "message": "Slot taken",
                "agent": "BookingAgent",
            }
        )
        return out

    monkeypatch.setattr("orchestration.mas_workflow.intent_agent", fake_intent)
    monkeypatch.setattr("orchestration.mas_workflow.availability_agent", fake_avail)
    monkeypatch.setattr("orchestration.mas_workflow.booking_agent", fake_booking)
    monkeypatch.setattr("orchestration.mas_workflow.notification_agent", capture_notification)

    out = pl.run_system("book anything")

    assert calls == []
    assert out["notification"]["status"] == "skipped"
    assert "appointments.json" in (out["notification"].get("message") or "")
    assert out.get("appointment") == {}
