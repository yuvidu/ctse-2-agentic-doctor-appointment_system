"""LangGraph workflow wiring (agents monkeypatched — no Ollama)."""

from __future__ import annotations

import orchestration.mas_workflow as mw
from orchestration.mas_workflow import build_graph


def test_build_graph_compiles() -> None:
    g = build_graph().compile()
    assert g is not None


def test_skip_notification_when_booking_not_confirmed(monkeypatch) -> None:
    calls: list[int] = []

    def capture_notification(s: dict) -> dict:
        calls.append(1)
        return s

    def fake_intent(s: dict) -> dict:
        return {"status": "complete", "intent": {"specialization": "X", "date": "2026-01-01"}}

    def fake_avail(s: dict, **kwargs: object) -> dict:
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

    monkeypatch.setattr(mw, "intent_agent", fake_intent)
    monkeypatch.setattr(mw, "availability_agent", fake_avail)
    monkeypatch.setattr(mw, "booking_agent", fake_booking)
    monkeypatch.setattr(mw, "notification_agent", capture_notification)

    from pipeline import run_system

    out = run_system("book anything")

    assert calls == []
    assert out["notification"]["status"] == "skipped"
    assert "appointments.json" in (out["notification"].get("message") or "")
    assert out.get("appointment") == {}


def test_skip_notification_when_availability_failed(monkeypatch) -> None:
    calls: list[int] = []

    def capture_notification(s: dict) -> dict:
        calls.append(1)
        return s

    def fake_intent(s: dict) -> dict:
        return {"status": "complete", "intent": {"specialization": "X", "date": "2026-01-01"}}

    def fake_avail(s: dict, **kwargs: object) -> dict:
        return {"status": "availability_failed", "errors": [], "availability": {}}

    monkeypatch.setattr(mw, "intent_agent", fake_intent)
    monkeypatch.setattr(mw, "availability_agent", fake_avail)
    monkeypatch.setattr(mw, "notification_agent", capture_notification)

    from pipeline import run_system

    out = run_system("book anything")

    assert calls == []
    assert out["notification"]["status"] == "skipped"
    assert out.get("appointment") == {}
