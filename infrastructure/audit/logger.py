import json
import os
from datetime import datetime, timezone
from infrastructure.tracing.tracer import trace_context
from common.logger import get_logger

logger = get_logger(__name__)

AUDIT_LOG_PATH = os.path.join("logs", "audit.jsonl")

class AuditLogger:
    """
    Immutable, append-only audit trail.
    Never delete audit history. Every critical action gets a permanent record.
    """
    
    @staticmethod
    def log(action: str, actor: str, details: dict = None):
        os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
        
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "actor": actor,
            "details": details or {},
        }
        record.update(trace_context())
        
        with open(AUDIT_LOG_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")
            
        logger.info(f"[Audit] {actor} -> {action}")
