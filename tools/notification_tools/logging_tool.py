from datetime import datetime
from typing import Any

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

    # Print to console
    print(f"[LOG] {log}")

    # Save to file
    with open("logs.txt", "a") as f:
        f.write(str(log) + "\n")