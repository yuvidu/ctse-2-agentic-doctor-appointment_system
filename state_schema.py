from typing import TypedDict, Dict, List, Optional


class Appointment(TypedDict):
    appointment_id: str
    user_name: str
    user_contact: str
    doctor: str
    specialization: str
    time_iso: str
    channel: str


class NotificationResult(TypedDict):
    status: str  # 'sent' or 'failed'
    channel: str
    message: str
    error: Optional[str]


class State(TypedDict):
    user_input: str
    intent: Dict
    doctor: str
    available_slots: List[str]
    appointment: Optional[Appointment]
    notification: Optional[NotificationResult]
    status: str
    errors: List[str]