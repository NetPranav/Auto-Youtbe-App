import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import logger
from database.database import init_db
from database.session import get_db_session
from providers.manager import ProviderManager
from learning_engine.engine import LearningEngine

def run_learning():
    logger.info("=== STARTING LEARNING INTELLIGENCE PIPELINE ===")
    
    init_db()
    
    provider_manager = ProviderManager()
    
    with get_db_session() as db:
        engine = LearningEngine(db, provider_manager)
        engine.run()
        
    logger.info("=== LEARNING INTELLIGENCE PIPELINE COMPLETED ===")

if __name__ == "__main__":
    run_learning()
