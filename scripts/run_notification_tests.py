"""Run pytest for notification-related tests from repo root."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "tests/test_notification_tool.py",
    "tests/test_provisional_appointment.py",
    "tests/test_notification_integration.py",
    "tests/test_notification_judge.py",
    "tests/test_booking_agent.py",
]


def main() -> int:
    cmd = [sys.executable, "-m", "pytest", *FILES, "-v"]
    return subprocess.call(cmd, cwd=_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
