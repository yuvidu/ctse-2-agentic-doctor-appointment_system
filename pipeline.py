"""Intent → Availability → Booking → Notification (importable by CLI, FastAPI, tests).

Orchestration is implemented with LangGraph (:mod:`orchestration.mas_workflow`).
"""

from __future__ import annotations

from orchestration.mas_workflow import run_mas_workflow


def run_system(user_input: str) -> dict:
    """Run Intent, Availability, Booking, then Notification when intent is complete."""
    return run_mas_workflow(user_input)
