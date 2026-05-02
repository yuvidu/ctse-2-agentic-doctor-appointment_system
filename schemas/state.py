"""TypedDict contracts for Availability and Intent→Availability bridge (CTSE MAS)."""

from __future__ import annotations

from typing import Any, TypedDict


class ErrorEntry(TypedDict):
    code: str
    message: str
    agent: str


class IntentPayload(TypedDict, total=False):
    """Structured intent for Availability (after bridge from Intent repo keys)."""

    specialty: str
    doctor_id: str
    preferred_date: str
    preferred_time_window: str
    location: str
    slot_preference_notes: str


class AvailabilitySlot(TypedDict):
    doctor_id: str
    start: str
    end: str
    location: str
    specialty: str


class OllamaSlotRanking(TypedDict, total=False):
    recommended_slot_indices: list[int]
    rationale: str
    model: str


class AvailabilityPayload(TypedDict, total=False):
    queried_at: str
    source: str
    filters_applied: dict[str, Any]
    available_slots: list[AvailabilitySlot]
    total_count: int
    ollama_ranking: OllamaSlotRanking


class NotificationPayload(TypedDict, total=False):
    """Mock notification result attached by ``notification_agent``."""

    status: str
    channel: str | None
    message: str
    error: str | None


class GlobalState(TypedDict, total=False):
    """Pipeline slice passed to ``availability_agent``."""

    user_input: str
    intent: IntentPayload
    missing_fields: list[str]
    errors: list[ErrorEntry]
    status: str
    availability: AvailabilityPayload
    notification: NotificationPayload
