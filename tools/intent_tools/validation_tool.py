from typing import Dict
import requests

def get_specializations():
    response = requests.get("http://localhost:8000/specializations")
    return response.json().get("data", [])

VALID_SPECIALIZATIONS = get_specializations()


def validate_input(data: Dict) -> Dict:
    errors = []

    if "specialization" in data:
        if data["specialization"] not in VALID_SPECIALIZATIONS:
            errors.append("Invalid specialization")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }