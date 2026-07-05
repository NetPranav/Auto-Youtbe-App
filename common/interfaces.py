from abc import ABC, abstractmethod
from typing import Any

class BaseEngine(ABC):
    """
    Base class for all execution engines.
    """
    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the primary logic for the engine."""
        pass

class BaseProvider(ABC):
    """
    Base class for external AI or Service Providers.
    """
    pass

class BaseRepository(ABC):
    """
    Base class for database repositories implementing CRUD.
    """
    pass
