import time
from database.session import get_db_session
from database.models import ProviderStatistic
from common import logger
from .models import TaskCategory

class ProviderStatistics:
    """
    Tracks and stores metrics for AI provider usage in the database.
    """
    @staticmethod
    def log_request(
        provider_name: str,
        model_used: str,
        request_type: str,
        task_category: TaskCategory,
        execution_time_ms: float,
        success: bool,
        tokens_used: int = 0,
        estimated_cost: float = 0.0
    ):
        try:
            with get_db_session() as db:
                stat = ProviderStatistic(
                    provider_name=provider_name,
                    model_used=model_used,
                    request_type=request_type,
                    task_category=task_category.value if hasattr(task_category, 'value') else str(task_category),
                    execution_time_ms=execution_time_ms,
                    success=success,
                    tokens_used=tokens_used,
                    estimated_cost=estimated_cost
                )
                db.add(stat)
                db.commit()
        except Exception as e:
            logger.error(f"[ProviderStatistics] Failed to log statistic: {e}")
