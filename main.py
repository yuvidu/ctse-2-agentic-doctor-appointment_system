"""CLI entry: full ``pipeline.run_system`` (Intent → Availability → Booking → Notification)."""

from __future__ import annotations

from pipeline import run_system


if __name__ == "__main__":
    while True:
        user_input = input("\nEnter request: ")
        result = run_system(user_input)
        print("\nFinal Output:")
        print(result)
