from typing import Dict

VALID_SPECIALIZATIONS = ["dentist", "cardiologist", "dermatologist"]

def validate_input(data: Dict) -> Dict:
    errors = []

    if "specialization" in data:
        if data["specialization"] not in VALID_SPECIALIZATIONS:
            errors.append("Invalid specialization")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }