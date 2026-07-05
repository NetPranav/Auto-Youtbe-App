import json
from typing import Any, Dict
from pathlib import Path
from .exceptions import ValidationError

def load_json(filepath: str) -> Dict[str, Any]:
    """Safely load a JSON file into a dict."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValidationError(f"File not found: {filepath}")
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in {filepath}: {e}")

def save_json(filepath: str, data: Dict[str, Any]) -> None:
    """Save a dictionary to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
