from typing import Any
from .exceptions import ValidationError

def require_not_none(value: Any, field_name: str) -> Any:
    """Raises ValidationError if value is None."""
    if value is None:
        raise ValidationError(f"Field '{field_name}' cannot be None.")
    return value

def require_string_not_empty(value: str, field_name: str) -> str:
    """Raises ValidationError if string is empty or None."""
    if not value or not str(value).strip():
        raise ValidationError(f"Field '{field_name}' cannot be empty.")
    return str(value).strip()
