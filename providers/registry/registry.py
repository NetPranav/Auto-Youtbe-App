from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class ModelInfo:
    model_id: str
    provider: str
    capabilities: List[str] = field(default_factory=list)
    context_length: Optional[int] = None
    available_endpoints: List[str] = field(default_factory=list)
    supported_features: List[str] = field(default_factory=list)
    is_available: bool = True
    last_checked: Optional[datetime] = None
    
    # Benchmarks
    avg_latency_ms: float = 0.0
    timeout_rate: float = 0.0
    reasoning_score: float = 0.0
    creativity_score: float = 0.0
    json_reliability: float = 0.0

class ModelRegistry:
    """
    In-memory store of model configurations and health metadata.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance._models = {}
        return cls._instance
        
    def add_model(self, model: ModelInfo):
        self._models[model.model_id] = model
        
    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        return self._models.get(model_id)
        
    def get_all_models(self) -> List[ModelInfo]:
        return list(self._models.values())
        
    def get_healthy_models(self) -> List[ModelInfo]:
        return [m for m in self._models.values() if m.is_available]
        
    def clear(self):
        self._models.clear()
