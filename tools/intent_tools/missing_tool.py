from typing import Dict, List

def detect_missing_fields(data: Dict) -> List[str]:
    required = ["specialization", "date", "time_preference"]
    return [f for f in required if f not in data or not data[f]]