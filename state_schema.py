"""Global orchestration state (Intent + pipeline extensions).

See also :mod:`schemas.state` for TypedDicts used by the Availability agent slice.
"""

from __future__ import annotations

from typing import Any, Dict, List, NotRequired, TypedDict


class State(TypedDict, total=False):
    """Runtime dict produced by ``run_system`` in ``main.py``."""

    user_input: str
    intent: Dict[str, Any]
    doctor: str
    available_slots: List[str]
    appointment: Dict[str, Any]
    status: str
    errors: List[Any]
    # After Availability agent
    availability: NotRequired[Dict[str, Any]]
    availability_status: NotRequired[str]
    availability_errors: NotRequired[List[Any]]
    availability_missing_fields: NotRequired[List[str]]
