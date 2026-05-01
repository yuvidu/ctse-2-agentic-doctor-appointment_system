import importlib.util
from pathlib import Path
import sys


def _load_tests_module():
    repo_root = Path(__file__).resolve().parent.parent
    # Ensure repo root is on sys.path so 'tools' and other modules import correctly
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    test_path = repo_root / "tests" / "test_notification_agent.py"
    spec = importlib.util.spec_from_file_location("test_notification_agent", str(test_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_all():
    mod = _load_tests_module()
    mod.test_format_message_contains_fields()
    print("test_format_message_contains_fields: OK")

    mod.test_send_notification_calls_logger_and_returns_sent()
    print("test_send_notification_calls_logger_and_returns_sent: OK")

    mod.test_send_notification_handles_logger_exception()
    print("test_send_notification_handles_logger_exception: OK")


if __name__ == "__main__":
    run_all()
