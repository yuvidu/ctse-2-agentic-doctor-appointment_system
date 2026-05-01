import json
import os
import re
import ollama
from typing import Dict, Any
from pydantic import BaseModel, ValidationError
from crewai import Agent

from tools.notification_tools.notification_tool import send_notification
from tools.notification_tools.logging_tool import log_event
from tools.notification_tools.storage_tool import save_appointment


class AppointmentModel(BaseModel):
    appointment_id: str
    user_name: str
    user_contact: str
    doctor: str
    specialization: str
    time_iso: str
    channel: str


def extract_json(text: str) -> dict:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return {}
    return {}


def notification_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Notification & Summary Agent.

    Reads `state['appointment']`, validates it, uses Ollama to generate a notification message,
    stores it using `save_appointment`, dispatches it using `send_notification`,
    and emits structured logs.
    """
    print("\n[Agent] Running Notification Agent...")
    log_event("NotificationAgent", "start", {"appointment": state.get("appointment")})

    appointment_data = state.get("appointment")
    if not appointment_data:
        err = "Missing appointment in state"
        log_event("NotificationAgent", "error", {"error": err})
        state.setdefault("errors", []).append(err)
        state["notification"] = {"status": "failed", "channel": None, "message": "", "error": err}
        state["status"] = "error"
        return state

    # 1. Pydantic Validation
    try:
        validated_appointment = AppointmentModel(**appointment_data)
    except ValidationError as e:
        err = f"Invalid appointment data: {str(e)}"
        log_event("NotificationAgent", "error", {"error": err})
        state.setdefault("errors", []).append(err)
        state["notification"] = {"status": "failed", "channel": None, "message": "", "error": err}
        state["status"] = "error"
        return state

    # 2. Generate Notification Message
    prompt_path = os.path.join(os.path.dirname(__file__), "notification_prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
    else:
        system_prompt = "You ONLY return valid JSON. No explanations."

    user_prompt = f"Generate notification JSON for this appointment state:\n{json.dumps({'appointment': validated_appointment.dict()})}"

    try:
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        content = response['message']['content']
        log_event("NotificationAgent", "llm_raw_output", content)
        llm_result = extract_json(content)
        if "notification" in llm_result:
            message = llm_result["notification"].get("message", "Appointment confirmed.")
        else:
            message = llm_result.get("message", "Appointment confirmed.")
    except Exception as e:
        log_event("NotificationAgent", "llm_error", str(e))
        message = f"Appointment Confirmed: ID {validated_appointment.appointment_id} with Dr. {validated_appointment.doctor} on {validated_appointment.time_iso}"

    # 3. Store Appointment Details
    save_appointment(validated_appointment.dict())

    # 4. Simulate Notification
    channel = validated_appointment.channel
    result = send_notification(validated_appointment.dict(), message=message, channel=channel, logger=log_event)

    state["notification"] = result
    state["status"] = "confirmed" if result.get("status") == "sent" else "error"

    log_event("NotificationAgent", "finish", {"notification": result})

    return state
