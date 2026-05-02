from __future__ import annotations

from integration.provisional_appointment import build_provisional_appointment


def test_build_provisional_from_availability_slots() -> None:
    state = {
        "user_input": "cardiology tomorrow",
        "intent": {
            "status": "complete",
            "intent": {
                "specialization": "Cardiology",
                "date": "2026-05-02",
                "time_preference": "morning",
            },
        },
        "availability": {
            "available_slots": [
                {
                    "doctor_id": "D1",
                    "start": "2026-05-02T09:00:00",
                    "end": "2026-05-02T10:00:00",
                    "location": "Colombo",
                    "specialty": "cardiology",
                }
            ],
        },
    }
    appt = build_provisional_appointment(state)
    assert appt["appointment_id"].startswith("PREVIEW-")
    assert appt["doctor"] == "D1"
    assert appt["time_iso"] == "2026-05-02T09:00:00"
    assert appt["specialization"] == "Cardiology"


def test_build_provisional_respects_existing_appointment() -> None:
    state = {
        "appointment": {
            "appointment_id": "REAL-1",
            "user_name": "A",
            "user_contact": "x",
            "doctor": "D",
            "specialization": "S",
            "time_iso": "2026-01-01T10:00:00",
            "channel": "email",
        }
    }
    appt = build_provisional_appointment(state)
    assert appt["appointment_id"] == "REAL-1"
