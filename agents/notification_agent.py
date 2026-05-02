"""Notification & Summary Agent — mock send + local storage (no Booking required)."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import ollama
from pydantic import BaseModel, ValidationError

from integration.provisional_appointment import build_provisional_appointment
from tools.notification_tools.notification_tool import send_notification
from tools.notification_tools.storage_tool import save_appointment
from utils.env_flags import mas_debug
from utils.logging_utils import log_event


class AppointmentModel(BaseModel):
    appointment_id: str
    user_name: str
    user_contact: str
    doctor: str
    specialization: str
    time_iso: str
    channel: str


def extract_json(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return {}
    return {}


def _llm_message_should_use_fallback(text: str) -> bool:
    """True when assistant text is empty, contradictory, or looks like a schema/tool error."""
    t = (text or "").strip().lower()
    if not t:
        return True
    needles = (
        "failed to send",
        "could not send",
        "unable to send",
        "notification failed",
        "send failed",
        "did not send",
        "missing required field",
        "validation error",
        "pydantic",
        "field required",
        "must be str",
        "invalid json",
        "error:",
    )
    return any(n in t for n in needles)


def _confirmation_fallback(validated: AppointmentModel) -> str:
    return (
        f"Appointment confirmed: ID {validated.appointment_id} — "
        f"{validated.user_name} with Dr. {validated.doctor} ({validated.specialization}) "
        f"on {validated.time_iso}"
    )


def notification_agent(state: dict[str, Any]) -> dict[str, Any]:
    """Format summary message, persist preview row, mock-send notification.

    Does **not** change top-level ``state['status']`` (Intent outcome stays ``complete`` / etc.).
    Writes ``state['notification']`` with ``sent`` / ``failed`` and optional error string.
    """
    if mas_debug():
        print("\n[Agent] Running Notification Agent...")

    log_event("NotificationAgent", "start", {"appointment": state.get("appointment")})

    appt_raw = state.get("appointment")
    if not isinstance(appt_raw, dict) or not appt_raw.get("appointment_id"):
        state["appointment"] = build_provisional_appointment(state)

    appointment_data = state["appointment"]

    try:
        validated = AppointmentModel(**appointment_data)
    except ValidationError as e:
        err = f"Invalid appointment data: {e!s}"
        log_event("NotificationAgent", "error", {"error": err})
        state["notification"] = {
            "status": "failed",
            "channel": None,
            "message": "",
            "error": err,
        }
        return state

    prompt_path = os.path.join(os.path.dirname(__file__), "notification_prompt.txt")
    if os.path.isfile(prompt_path):
        with open(prompt_path, encoding="utf-8") as f:
            system_prompt = f.read()
    else:
        system_prompt = "You ONLY return valid JSON. No explanations."

    payload = {"appointment": validated.model_dump()}
    user_prompt = f"Generate notification JSON for this appointment state:\n{json.dumps(payload)}"

    model = os.environ.get("OLLAMA_MODEL", "llama3.2:3b").strip() or "llama3.2:3b"
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response["message"]["content"]
        log_event("NotificationAgent", "llm_raw_output", {"content": content[:2000]})
        llm_result = extract_json(content)
        if "notification" in llm_result and isinstance(llm_result["notification"], dict):
            message = llm_result["notification"].get("message", "Appointment confirmed.")
        else:
            message = llm_result.get("message", "Appointment confirmed.")
    except Exception as e:  # noqa: BLE001
        log_event("NotificationAgent", "llm_error", {"error": str(e)})
        message = (
            f"Summary: ID {validated.appointment_id} — Dr. {validated.doctor} "
            f"({validated.specialization}) at {validated.time_iso}"
        )

    save_appointment(validated.model_dump())

    channel = validated.channel
    result = send_notification(
        validated.model_dump(),
        message=str(message),
        channel=channel,
        logger=log_event,
    )
    out = dict(result)
    if out.get("status") == "sent" and _llm_message_should_use_fallback(out.get("message", "")):
        out["message"] = _confirmation_fallback(validated)
        log_event("NotificationAgent", "message_sanitized", {"reason": "llm_unusable_notification_copy"})
    state["notification"] = out
    log_event("NotificationAgent", "finish", {"notification": dict(out)})
    return state
