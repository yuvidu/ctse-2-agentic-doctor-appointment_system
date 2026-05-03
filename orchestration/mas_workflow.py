"""LangGraph StateGraph: Intent → Availability → Booking → Notification (conditional routing)."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agents.availability_agent import availability_agent
from agents.booking_agent import booking_agent
from agents.intent_agent import intent_agent
from agents.notification_agent import notification_agent
from integration.intent_to_availability_state import global_state_from_intent_repo
from orchestration.state_helpers import (
    SCHEDULES_PATH,
    booking_failure_notification_message,
    normalize_appointment_for_notification,
)
from state_schema import State

_compiled: object | None = None


def clear_compiled_graph() -> None:
    """Drop cached compiled graph (use in tests after monkeypatching node dependencies)."""
    global _compiled
    _compiled = None


def _node_intent(state: State) -> State:
    work: dict = {
        "user_input": state["user_input"],
        "intent": state.get("intent") or {},
        "doctor": state.get("doctor") or "",
        "available_slots": list(state.get("available_slots") or []),
        "appointment": state.get("appointment") or {},
        "status": state.get("status") or "",
        "errors": list(state.get("errors") or []),
    }
    intent_response = intent_agent(work)
    out: dict = {**dict(state)}
    out["intent"] = intent_response
    out["status"] = intent_response.get("status", "")
    if isinstance(intent_response.get("errors"), list):
        out["errors"] = intent_response["errors"]
    return out  # type: ignore[return-value]


def _route_intent(state: State) -> str:
    ir = state.get("intent")
    if isinstance(ir, dict) and ir.get("status") == "complete":
        return "availability"
    return END


def _node_availability(state: State) -> State:
    mas_state = global_state_from_intent_repo(dict(state))
    avail_out = availability_agent(mas_state, schedules_path=SCHEDULES_PATH)
    out: dict = {**dict(state)}
    out["availability"] = avail_out.get("availability")
    out["availability_status"] = avail_out.get("status")
    if avail_out.get("errors"):
        out["availability_errors"] = avail_out["errors"]
    if avail_out.get("missing_fields"):
        out["availability_missing_fields"] = avail_out["missing_fields"]
    slots = (avail_out.get("availability") or {}).get("available_slots") or []
    out["available_slots"] = [
        f"{s.get('doctor_id', '')} | {s.get('start', '')} – {s.get('end', '')} | {s.get('location', '')}"
        for s in slots
    ]
    if slots:
        out["doctor"] = str(slots[0].get("doctor_id", ""))
    return out  # type: ignore[return-value]


def _node_booking_normalize(state: State) -> State:
    s: dict = {**dict(state)}
    s = booking_agent(s)
    normalize_appointment_for_notification(s)
    bk = s.get("booking") or {}
    if bk.get("status") and bk.get("status") != "confirmed":
        s["notification"] = {
            "status": "skipped",
            "channel": None,
            "message": booking_failure_notification_message(s),
            "error": None,
        }
        s["appointment"] = {}
    return s  # type: ignore[return-value]


def _route_booking(state: State) -> str:
    n = state.get("notification") or {}
    if n.get("status") == "skipped":
        return END
    return "notification"


def _node_notification(state: State) -> State:
    s: dict = {**dict(state)}
    return notification_agent(s)  # type: ignore[return-value]


def build_graph() -> StateGraph:
    """Compile the multi-agent workflow (call :func:`compile` on the result)."""
    g = StateGraph(State)
    g.add_node("intent", _node_intent)
    g.add_node("availability", _node_availability)
    g.add_node("booking_normalize", _node_booking_normalize)
    g.add_node("notification", _node_notification)
    g.add_edge(START, "intent")
    g.add_conditional_edges(
        "intent",
        _route_intent,
        {"availability": "availability", END: END},
    )
    g.add_edge("availability", "booking_normalize")
    g.add_conditional_edges(
        "booking_normalize",
        _route_booking,
        {"notification": "notification", END: END},
    )
    g.add_edge("notification", END)
    return g


def get_compiled_graph():
    global _compiled
    if _compiled is None:
        _compiled = build_graph().compile()
    return _compiled


def run_mas_workflow(user_input: str) -> dict:
    """Run the full MAS pipeline (same contract as the former imperative ``run_system``)."""
    initial: State = {
        "user_input": user_input,
        "intent": {},
        "doctor": "",
        "available_slots": [],
        "appointment": {},
        "status": "",
        "errors": [],
    }
    return get_compiled_graph().invoke(initial)  # type: ignore[no-any-return]
