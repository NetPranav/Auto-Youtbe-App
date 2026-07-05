import time
from functools import wraps
from typing import Callable, Any
from .logger import logger

def with_retry(max_retries: int = 3, delay: int = 2, backoff: int = 2) -> Callable:
    """
    Decorator for exponential backoff retries.
    Usage:
        @with_retry(max_retries=3, delay=2, backoff=2)
        def my_network_call():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"Function '{func.__name__}' failed after {max_retries} attempts. Last Error: {e}")
                        raise
                    logger.warning(f"Attempt {attempt}/{max_retries} failed for '{func.__name__}': {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator
