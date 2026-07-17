import time
import json
import os
import functools
from datetime import datetime, timezone
from infrastructure.tracing.tracer import trace_context
from common import logger



METRICS_LOG_PATH = os.path.join("logs", "metrics.jsonl")

def _append_metric(metric: dict):
    """Append a metric record to the structured JSONL log."""
    os.makedirs(os.path.dirname(METRICS_LOG_PATH), exist_ok=True)
    metric["timestamp"] = datetime.now(timezone.utc).isoformat()
    metric.update(trace_context())
    with open(METRICS_LOG_PATH, "a") as f:
        f.write(json.dumps(metric) + "\n")

def track_metric(metric_name: str):
    """Decorator that measures execution time and logs it as a metric."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = None
            success = True
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                elapsed = time.perf_counter() - start
                _append_metric({
                    "metric": metric_name,
                    "duration_sec": round(elapsed, 4),
                    "success": success
                })
                logger.debug(f"[Metrics] {metric_name}: {elapsed:.4f}s (success={success})")
        return wrapper
    return decorator

def record_metric(name: str, value: float, unit: str = ""):
    """Manually record a single metric data point."""
    _append_metric({
        "metric": name,
        "value": value,
        "unit": unit
    })
