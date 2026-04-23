from typing import TypedDict, Dict, List

class State(TypedDict):
    user_input: str
    intent: Dict
    doctor: str
    available_slots: List[str]
    appointment: Dict
    status: str
    errors: List[str]