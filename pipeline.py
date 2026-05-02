"""Intent → Availability pipeline (importable by CLI, FastAPI, tests)."""

from __future__ import annotations

from pathlib import Path

from agents.availability_agent import availability_agent
from agents.booking_agent import booking_agent
from agents.crew_ai.crewai_agents import CREWAI_VERBOSE_FLAG, intent_agent_ai
from agents.intent_agent import intent_agent
from crewai import Crew, Task
from integration.intent_to_availability_state import global_state_from_intent_repo

_REPO_ROOT = Path(__file__).resolve().parent
_SCHEDULES = _REPO_ROOT / "data" / "sample_schedules.json"


def run_system(user_input: str) -> dict:
    """Run Intent agent, then Availability when intent is complete."""
    state: dict = {
        "user_input": user_input,
        "intent": {},
        "doctor": "",
        "available_slots": [],
        "appointment": {},
        "status": "",
        "errors": [],
    }

    intent_task = Task(
        description=f"Extract intent from: {user_input}",
        agent=intent_agent_ai,
        expected_output="Structured JSON",
    )
    crew = Crew(
        agents=[intent_agent_ai],
        tasks=[intent_task],
        verbose=CREWAI_VERBOSE_FLAG,
    )
    crew.kickoff()

    intent_response = intent_agent(state)
    state["intent"] = intent_response
    state["status"] = intent_response.get("status", "")
    if isinstance(intent_response.get("errors"), list):
        state["errors"] = intent_response["errors"]

    if intent_response.get("status") != "complete":
        return state

    mas_state = global_state_from_intent_repo(state)
    avail_out = availability_agent(mas_state, schedules_path=_SCHEDULES)

    state["availability"] = avail_out.get("availability")
    state["availability_status"] = avail_out.get("status")
    if avail_out.get("errors"):
        state["availability_errors"] = avail_out["errors"]
    if avail_out.get("missing_fields"):
        state["availability_missing_fields"] = avail_out["missing_fields"]

    slots = (avail_out.get("availability") or {}).get("available_slots") or []
    state["available_slots"] = [
        f"{s.get('doctor_id', '')} | {s.get('start', '')} – {s.get('end', '')} | {s.get('location', '')}"
        for s in slots
    ]
    if slots:
        state["doctor"] = str(slots[0].get("doctor_id", ""))

    if avail_out.get("status") == "availability_ok":
        final_state = booking_agent(avail_out)
        state["appointment"] = final_state.get("appointment")
        state["status"] = final_state.get("status")
        if final_state.get("errors"):
            # Append any new errors from the booking agent
            existing_errors = state.get("errors", [])
            new_errors = [e for e in final_state["errors"] if e not in existing_errors]
            state["errors"].extend(new_errors)

    return state
