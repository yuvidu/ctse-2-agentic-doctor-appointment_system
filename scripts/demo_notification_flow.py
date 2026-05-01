from pathlib import Path
import sys
import json

# Ensure repo root is importable
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from agents.notification_agent import notification_agent


def main():
    state = {
        "user_input": "Book dentist tomorrow",
        "intent": {},
        "doctor": "Smith",
        "available_slots": ["2026-05-03T10:00:00"],
        "appointment": {
            "appointment_id": "DEMO123",
            "user_name": "Demo User",
            "user_contact": "+10000000000",
            "doctor": "Smith",
            "specialization": "Dentist",
            "time_iso": "2026-05-03T10:00:00",
            "channel": "sms",
        },
        "status": "pending",
        "errors": [],
    }

    print("Running notification agent demo...")
    new_state = notification_agent(state)
    print("Resulting state:")
    print(json.dumps(new_state, indent=2))


if __name__ == "__main__":
    main()
