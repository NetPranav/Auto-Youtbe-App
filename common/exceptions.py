"""
Centralized exception hierarchy.
All engines must use these specific exceptions for standard error handling.
"""

class BaseAutomateError(Exception):
    """Base exception for all system-related errors."""
    pass

class ConfigurationError(BaseAutomateError):
    """Raised when environment variables or configs are invalid."""
    pass

class DatabaseError(BaseAutomateError):
    """Raised when a database operation fails."""
    pass

class AIProviderError(BaseAutomateError):
    """Raised when an external AI provider (LLM, etc.) fails."""
    pass

class AssetGenerationError(BaseAutomateError):
    """Raised when fetching images, generating audio, etc. fails."""
    pass

class VideoRenderError(BaseAutomateError):
    """Raised when FFmpeg or video stitching fails."""
    pass

class UploadError(BaseAutomateError):
    """Raised when YouTube API uploading fails."""
    pass

class ValidationError(BaseAutomateError):
    """Raised when data validation fails."""
    pass
