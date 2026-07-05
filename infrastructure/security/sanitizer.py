import re
from common.logger import get_logger

logger = get_logger(__name__)

# Patterns that match common secret formats
SECRET_PATTERNS = [
    re.compile(r'(nvapi-[A-Za-z0-9_-]+)', re.IGNORECASE),
    re.compile(r'(sk-[A-Za-z0-9_-]+)', re.IGNORECASE),
    re.compile(r'(AIza[A-Za-z0-9_-]+)', re.IGNORECASE),
    re.compile(r'(ya29\.[A-Za-z0-9_-]+)', re.IGNORECASE),
]

def redact_secrets(text: str) -> str:
    """Scrub known secret patterns from a string before logging."""
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(lambda m: m.group(0)[:6] + "****REDACTED****", text)
    return text

def validate_env_secrets(env_vars: dict) -> list:
    """
    Validates that critical secrets are present and non-empty.
    Returns a list of missing variable names.
    """
    required = ["NVIDIA_API_KEY", "NVIDIA_BASE_URL"]
    missing = []
    for var in required:
        val = env_vars.get(var, "")
        if not val or val.strip() == "":
            missing.append(var)
    if missing:
        logger.warning(f"[Security] Missing environment secrets: {missing}")
    return missing
