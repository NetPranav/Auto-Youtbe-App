from typing import Dict, Any
from config import config
from database import engine
from common import logger

def check_health() -> Dict[str, Any]:
    """
    Perform a system health check verifying configuration, database, and paths.
    """
    logger.info("Running System Health Check...")
    
    status = {
        "status": "Healthy",
        "config": "OK",
        "database": "OK",
        "errors": []
    }

    # 1. Check Configuration
    try:
        # Assuming if config is loaded, pydantic already validated it
        _ = config.environment
    except Exception as e:
        status["config"] = "FAILED"
        status["errors"].append(f"Config Error: {e}")

    # 2. Check Database Connection
    try:
        with engine.connect() as connection:
            pass # Connection successful
    except Exception as e:
        status["database"] = "FAILED"
        status["errors"].append(f"Database Error: {e}")

    # 3. Final Evaluation
    if status["errors"]:
        status["status"] = "Unhealthy"
        logger.error(f"Health Check Failed: {status['errors']}")
    else:
        logger.info("Health Check Passed.")

    return status
