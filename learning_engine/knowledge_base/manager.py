import json
import os
from typing import List, Dict
from sqlalchemy.orm import Session
from database.models import StrategyRecommendation, KnowledgeEntry
from common import logger



class KnowledgeManager:
    def __init__(self, db_session: Session, strategy_file: str = "data/strategy.json"):
        self.db = db_session
        self.strategy_file = strategy_file
        
    def save_recommendations(self, report_id: str, recommendations: List[Dict[str, str]]):
        logger.info(f"[KnowledgeManager] Storing {len(recommendations)} recommendations into Knowledge Base.")
        
        for rec in recommendations:
            db_rec = StrategyRecommendation(
                report_id=report_id,
                target_engine=rec["target_engine"],
                recommendation_text=rec["recommendation_text"]
            )
            self.db.add(db_rec)
            
            # Also store as an abstract knowledge entry
            entry = KnowledgeEntry(
                category=rec["target_engine"],
                insight=rec["recommendation_text"]
            )
            self.db.add(entry)
            
        self.db.commit()
        
    def compile_strategy_json(self):
        logger.info("[KnowledgeManager] Re-compiling global strategy.json for other engines...")
        
        # We fetch the latest confident knowledge entries and dump them to JSON
        entries = self.db.query(KnowledgeEntry).order_by(KnowledgeEntry.created_at.desc()).limit(20).all()
        
        strategy = {
            "RESEARCH": [],
            "CONTENT": [],
            "ASSET": [],
            "PUBLISHER": []
        }
        
        for e in entries:
            if e.category in strategy:
                strategy[e.category].append(e.insight)
                
        # Write to JSON
        os.makedirs(os.path.dirname(self.strategy_file), exist_ok=True)
        with open(self.strategy_file, "w") as f:
            json.dump(strategy, f, indent=4)
            
        logger.info(f"[KnowledgeManager] Successfully updated {self.strategy_file}")
