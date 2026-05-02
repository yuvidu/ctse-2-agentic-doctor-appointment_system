"""CLI demo: run Notification agent on a sample state (repo root on sys.path)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from agents.notification_agent import notification_agent  # noqa: E402


def main() -> None:
    state: dict = {
        "user_input": "Book dentist tomorrow",
        "intent": {},
        "doctor": "Smith",
        "available_slots": ["2026-05-03T10:00:00"],
        "appointment": {
            "appointment_id": "DEMO123",
            "user_name": "Demo User",
            "user_contact": "+10000000000",
            "doctor": "Smith",
            "specialization": "Dentistry",
            "time_iso": "2026-05-03T10:00:00",
            "channel": "sms",
        },
        "status": "complete",
        "errors": [],
    }

    print("Running notification_agent demo...")
    new_state = notification_agent(state)
    print(json.dumps(new_state, indent=2, default=str))


if __name__ == "__main__":
    main()
