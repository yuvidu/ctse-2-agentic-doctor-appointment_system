"""CrewAI agent stubs for reference (prompt personas). Runtime orchestration uses LangGraph — see ``orchestration/mas_workflow.py``."""

import os

from crewai import Agent, LLM


def crewai_verbose() -> bool:
    """Rich panels / step logs from CrewAI. Off by default; set CREWAI_VERBOSE=1 to enable."""
    return os.environ.get("CREWAI_VERBOSE", "").strip().lower() in ("1", "true", "yes")


# Read once at import (restart uvicorn after changing CREWAI_VERBOSE).
CREWAI_VERBOSE_FLAG = crewai_verbose()

ollama_llm = LLM(
    provider="ollama",
    model="llama3.2:3b",
    base_url="http://localhost:11434",
)

intent_agent_ai = Agent(
    role="Intent Analyzer",
    goal="Extract structured medical appointment intent",
    backstory="Expert in understanding user medical requests",
    verbose=CREWAI_VERBOSE_FLAG,
    llm=ollama_llm
)

availability_agent_ai = Agent(
    role="Availability Finder",
    goal="Find available doctors and slots",
    backstory="Knows doctor schedules",
    verbose=CREWAI_VERBOSE_FLAG,
    llm=ollama_llm
)

booking_agent_ai = Agent(
    role="Booking Manager",
    goal="Book appointment safely",
    backstory="Handles scheduling and conflicts",
    verbose=CREWAI_VERBOSE_FLAG,
    llm=ollama_llm
)

notification_agent_ai = Agent(
    role="Notification Manager",
    goal="Send appointment notifications",
    backstory="Handles sending notifications",
    verbose=CREWAI_VERBOSE_FLAG,
    llm=ollama_llm
)