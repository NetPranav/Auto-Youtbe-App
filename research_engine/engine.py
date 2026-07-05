from typing import Any, Dict, Optional
from common import logger
from common.interfaces import BaseEngine
from config import config

from .article_collector import ArticleCollector
from .article_normalizer import ArticleNormalizer
from .topic_extractor import TopicExtractor
from .duplicate_detector import DuplicateDetector
from .novelty_analyzer import NoveltyAnalyzer
from .topic_ranker import TopicRanker
from .topic_selector import TopicSelector
from .research_repository import ResearchRepository
from .models import RankedTopic

class ResearchEngine(BaseEngine):
    """
    Facade for the entire Research Phase.
    """
    def __init__(self, ai_provider: Any = None):
        if not ai_provider:
            from providers.manager import ProviderManager
            ai_provider = ProviderManager().get_llm_provider()
            
        self.ai = ai_provider
        self.repo = ResearchRepository()
        
        # Load sources from config
        sources = [s.strip() for s in config.research_enabled_sources.split(',')]
        
        self.collector = ArticleCollector(sources, config.research_max_articles_per_source)
        self.normalizer = ArticleNormalizer()
        self.extractor = TopicExtractor(self.ai)
        self.duplicate_detector = DuplicateDetector(self.ai)
        self.novelty_analyzer = NoveltyAnalyzer(self.ai)
        self.ranker = TopicRanker()
        self.selector = TopicSelector(self.ai)

    def run(self) -> Optional[Dict[str, Any]]:
        """
        Executes the full research pipeline.
        Returns the approved topic data or None.
        """
        logger.info("=== Starting Research Engine ===")
        session_id = self.repo.create_session()
        
        try:
            # 1. Collect
            collection_result = self.collector.collect()
            self.repo.save_stats(session_id, collection_result["stats"])
            
            # 2. Normalize
            normalized = self.normalizer.normalize(collection_result["articles"])
            self.repo.save_articles(session_id, normalized)
            
            # 3. Extract & Deduplicate & Rank
            past_topics = self.repo.get_past_topics()
            ranked_topics: list[RankedTopic] = []
            
            for article in normalized:
                # Extract
                candidate = self.extractor.extract(article)
                if not candidate:
                    continue
                    
                # Deduplicate
                if self.duplicate_detector.is_duplicate(candidate, past_topics):
                    continue
                    
                # Analyze Novelty
                novelty = self.novelty_analyzer.analyze(candidate)
                
                # Rank
                score = self.ranker.rank(candidate, novelty)
                
                # Add to ranked pool
                ranked_topics.append(RankedTopic(topic_id="", candidate=candidate, score=score))
                
            # 4. Select Best
            best_topic = self.selector.select(ranked_topics)
            
            # 5. Save all processed topics, mark the best one as approved
            approved_topic_id = None
            for ranked in ranked_topics:
                is_approved = (best_topic and ranked.candidate.title == best_topic.candidate.title)
                topic_id = self.repo.save_topic(session_id, ranked.candidate, ranked.score, is_approved)
                if is_approved:
                    approved_topic_id = topic_id
            
            self.repo.complete_session(session_id, "COMPLETED")
            logger.info("=== Research Engine Completed Successfully ===")
            
            if best_topic:
                return {
                    "topic_id": approved_topic_id,
                    "candidate": best_topic.candidate.model_dump()
                }
            return None

        except Exception as e:
            logger.error(f"Research Engine Failed: {e}", exc_info=True)
            self.repo.complete_session(session_id, "FAILED")
            return None
