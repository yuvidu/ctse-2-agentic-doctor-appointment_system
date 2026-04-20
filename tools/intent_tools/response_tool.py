from typing import List, Dict

def build_response(missing: List[str], errors: List[str], data: Dict) -> Dict:

    if missing:
        return {
            "status": "incomplete",
            "missing_fields": missing
        }

    if errors:
        return {
            "status": "error",
            "errors": errors
        }

    return {
        "status": "complete",
        "intent": data
    }