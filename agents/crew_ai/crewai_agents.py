"""CrewAI runtime path for backend verification and logging."""

from __future__ import annotations

import os
from typing import Any

from crewai import Agent, Crew, LLM, Task


def crewai_verbose() -> bool:
    """Rich panels / step logs from CrewAI. Off by default; set CREWAI_VERBOSE=1 to enable."""
    return os.environ.get("CREWAI_VERBOSE", "").strip().lower() in ("1", "true", "yes")


def _build_agents() -> tuple[Any, Any, Any, Any]:
    verbose_flag = crewai_verbose()
    llm = LLM(
        provider="ollama",
        model="llama3.2:3b",
        base_url="http://localhost:11434",
    )
    intent_agent_ai = Agent(
        role="Intent Analyzer",
        goal="Extract structured medical appointment intent",
        backstory="Expert in understanding user medical requests",
        verbose=verbose_flag,
        llm=llm,
    )
    availability_agent_ai = Agent(
        role="Availability Finder",
        goal="Find available doctors and slots",
        backstory="Knows doctor schedules",
        verbose=verbose_flag,
        llm=llm,
    )
    booking_agent_ai = Agent(
        role="Booking Manager",
        goal="Book appointment safely",
        backstory="Handles scheduling and conflicts",
        verbose=verbose_flag,
        llm=llm,
    )
    notification_agent_ai = Agent(
        role="Notification Manager",
        goal="Send appointment notifications",
        backstory="Handles sending notifications",
        verbose=verbose_flag,
        llm=llm,
    )
    return intent_agent_ai, availability_agent_ai, booking_agent_ai, notification_agent_ai


def run_crewai_runtime(user_input: str) -> dict[str, Any]:
    """Run a real CrewAI kickoff so backend can emit CrewAI runtime logs."""
    intent_agent_ai, availability_agent_ai, booking_agent_ai, notification_agent_ai = _build_agents()

    task1 = Task(
        description=(
            "Extract specialization, date, and time preference from this user request: {user_input}. "
            "Return JSON only."
        ),
        expected_output='{"specialization":"...","date":"...","time_preference":"..."}',
        agent=intent_agent_ai,
    )
    task2 = Task(
        description=(
            "Using previous result, propose likely doctor availability in JSON with "
            "fields doctor and available_slots."
        ),
        expected_output='{"doctor":"...","available_slots":["..."]}',
        agent=availability_agent_ai,
    )
    task3 = Task(
        description="Choose best slot and produce booking JSON.",
        expected_output='{"status":"confirmed|failed","appointment_id":"...","details":{}}',
        agent=booking_agent_ai,
    )
    task4 = Task(
        description="Generate final user-friendly confirmation message.",
        expected_output='{"message":"...","notification_status":"sent|skipped"}',
        agent=notification_agent_ai,
    )

    crew = Crew(
        agents=[intent_agent_ai, availability_agent_ai, booking_agent_ai, notification_agent_ai],
        tasks=[task1, task2, task3, task4],
        verbose=crewai_verbose(),
    )
    result = crew.kickoff(inputs={"user_input": user_input})
    return {
        "mode": "crewai_runtime",
        "raw_result": str(result),
    }