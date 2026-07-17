import os
import sys
from loguru import logger

# Ensure the root directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import init_db
from research_engine.engine import ResearchEngine

def main():
    logger.info("Initializing Database...")
    init_db()
    
    logger.info("Starting Research Engine Test...")
    engine = ResearchEngine()
    result = engine.run()
    
    if result:
        logger.success(f"Selected Topic ID: {result['topic_id']}")
        logger.success("Best Topic Candidate:")
        
        # Pretty print the topic details
        candidate = result['candidate']
        print("-" * 50)
        print(f"Title: {candidate.get('title')}")
        print(f"Angle: {candidate.get('angle')}")
        print(f"Target Audience: {candidate.get('target_audience')}")
        print(f"Hook: {candidate.get('hook')}")
        print(f"Key Points: {candidate.get('key_points', [])}")
        print("-" * 50)
        
    else:
        logger.warning("Research Engine finished but did not select any topic.")

if __name__ == "__main__":
    main()
