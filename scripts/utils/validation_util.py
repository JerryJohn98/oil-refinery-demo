from typing import Any, Dict, List


class ValidationError(Exception):
    """Custom exception for validation errors."""

    def __init__(self, status: bool, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def validate_payload(payload: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that all mandatory fields are present and not empty in the payload.
    """
    errors = []
    for field in required_fields:
        value = payload.get(field)
        if value in (None, "", [], {}):
            errors.append(f"{field} is mandatory and cannot be empty.")

    if errors:
        # Raise ValidationError with a custom message and status
        raise ValidationError(status=False, message=", ".join(errors))
