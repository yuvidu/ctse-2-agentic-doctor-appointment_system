"""Map Intent-repo ``state['intent']`` onto :class:`schemas.state.GlobalState` for Availability."""

from __future__ import annotations

from typing import Any

from schemas.state import ErrorEntry, GlobalState

_MISSING_FIELD_BRIDGE: dict[str, str] = {
    "specialization": "intent.specialty",
    "date": "intent.preferred_date",
    "time_preference": "intent.preferred_time_window",
}


def _norm_time_window(raw: Any) -> str:
    if raw is None:
        return "any"
    s = str(raw).strip().lower()
    if not s:
        return "any"
    if any(x in s for x in ("afternoon", "evening", "after lunch", "pm")):
        return "afternoon"
    if any(x in s for x in ("morning", "am", "early")):
        return "morning"
    if s in ("any", "either", "flexible", "whatever"):
        return "any"
    return "any"


def intent_repo_block_to_mas_intent(intent_block: dict[str, Any]) -> dict[str, Any]:
    """Turn ``state['intent']`` from the Intent repo into Availability ``intent`` keys."""
    if not intent_block:
        return {}
    inner = intent_block.get("intent")
    payload_src: dict[str, Any] = inner if isinstance(inner, dict) else intent_block

    spec = payload_src.get("specialization") or payload_src.get("specialty")
    date_val = payload_src.get("date") or payload_src.get("preferred_date")
    time_pref = payload_src.get("time_preference") or payload_src.get("preferred_time_window")
    doctor_id = payload_src.get("doctor_id")
    notes = payload_src.get("slot_preference_notes") or payload_src.get("notes")

    out: dict[str, Any] = {}
    if spec:
        out["specialty"] = str(spec).strip().lower()
    if date_val:
        out["preferred_date"] = str(date_val).strip()
    if time_pref is not None and str(time_pref).strip():
        out["preferred_time_window"] = _norm_time_window(time_pref)
    if doctor_id:
        out["doctor_id"] = str(doctor_id).strip()
    if notes:
        out["slot_preference_notes"] = str(notes).strip()
    return out


def global_state_from_intent_repo(state: dict[str, Any]) -> GlobalState:
    """Build :class:`GlobalState` from ``run_system`` dict after ``intent_agent`` has run."""
    ib = state.get("intent") or {}
    mf_raw: list[str] = []
    if ib.get("status") == "incomplete" and isinstance(ib.get("missing_fields"), list):
        mf_raw = [str(x) for x in ib["missing_fields"]]
    mf_norm = [_MISSING_FIELD_BRIDGE.get(x, x) for x in mf_raw]

    errors: list[ErrorEntry] = []
    if ib.get("status") == "error" and isinstance(ib.get("errors"), list):
        for e in ib["errors"]:
            errors.append({"code": "INTENT_VALIDATION", "message": str(e), "agent": "IntentAgent"})

    return {
        "user_input": str(state.get("user_input", "")),
        "intent": intent_repo_block_to_mas_intent(ib),
        "missing_fields": mf_norm,
        "errors": errors,
    }
