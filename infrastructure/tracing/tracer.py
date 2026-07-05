import uuid
import contextvars
from common.logger import get_logger

logger = get_logger(__name__)

# Context variable that holds the current trace ID for the entire workflow
_trace_id: contextvars.ContextVar[str] = contextvars.ContextVar('trace_id', default='NO_TRACE')
_workflow_id: contextvars.ContextVar[str] = contextvars.ContextVar('workflow_id', default='NO_WORKFLOW')

def new_trace(workflow_id: str = None) -> str:
    """Start a new distributed trace. Returns the generated trace ID."""
    tid = str(uuid.uuid4())
    _trace_id.set(tid)
    if workflow_id:
        _workflow_id.set(workflow_id)
    logger.info(f"[Tracer] New trace started: {tid} (Workflow: {workflow_id})")
    return tid

def get_trace_id() -> str:
    return _trace_id.get()

def get_workflow_id() -> str:
    return _workflow_id.get()

def trace_context() -> dict:
    """Returns a dict with trace metadata for structured logging."""
    return {
        "trace_id": get_trace_id(),
        "workflow_id": get_workflow_id()
    }
