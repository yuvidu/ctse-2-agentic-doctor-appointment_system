from datetime import datetime
from typing import Any

from utils.env_flags import mas_debug


def log_event(agent: str, step: str, data: Any) -> None:
    """
    Log agent activity with timestamp.

    Args:
        agent (str): Name of the agent or tool
        step (str): Step description (input, parsing, validation, etc.)
        data (Any): Data to log
    """

    log = {
        "time": datetime.now().isoformat(),
        "agent": agent,
        "step": step,
        "data": str(data)
    }

    if not mas_debug():
        return

    print(f"[LOG] {log}")

    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(str(log) + "\n")