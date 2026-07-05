from enum import Enum

class WorkflowState(str, Enum):
    """
    Defines the possible states of a video project in the Orchestrator.
    """
    INITIALIZED = "INITIALIZED"
    RESEARCHING = "RESEARCHING"
    RESEARCH_READY = "RESEARCH_READY"
    SCRIPTING = "SCRIPTING"
    SCRIPT_READY = "SCRIPT_READY"
    GATHERING_ASSETS = "GATHERING_ASSETS"
    ASSETS_READY = "ASSETS_READY"
    RENDERING = "RENDERING"
    VIDEO_READY = "VIDEO_READY"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
