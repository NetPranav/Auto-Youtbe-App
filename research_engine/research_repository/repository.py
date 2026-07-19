from typing import List, Dict, Any, Optional
from common.interfaces import BaseRepository
from common.exceptions import DatabaseError
from common import logger
from database.session import get_db_session
from database.models import ResearchSession, ProcessedSource, Article, Topic, TopicScore

class ResearchRepository(BaseRepository):
    """
    Handles all DB CRUD operations for the Research Engine.
    """

    def create_session(self) -> str:
        """Creates a new ResearchSession and returns its ID."""
        with get_db_session() as db:
            session = ResearchSession()
            db.add(session)
            db.flush()
            return session.id

    def save_stats(self, session_id: str, stats: List[Dict[str, Any]]) -> None:
        """Saves ProcessedSource stats."""
        with get_db_session() as db:
            for stat in stats:
                ps = ProcessedSource(
                    session_id=session_id,
                    source_name=stat["source_name"],
                    articles_found=stat["articles_found"],
                    errors=stat.get("errors")
                )
                db.add(ps)

    def save_articles(self, session_id: str, articles: List[Any]) -> None:
        """Saves normalized articles."""
        with get_db_session() as db:
            for art in articles:
                existing = db.query(Article).filter(Article.url == art.url).first()
                if not existing:
                    db_art = Article(
                        session_id=session_id,
                        title=art.title,
                        url=art.url,
                        source=art.source,
                        publication_date=art.publication_date,
                        author=art.author,
                        summary=art.summary,
                        full_text=art.full_text,
                        categories=art.categories,
                        tags=art.tags
                    )
                    db.add(db_art)

    def get_past_topics(self) -> List[Topic]:
        """Fetches previously extracted topics for duplicate detection."""
        with get_db_session() as db:
            # Querying all topics for now. In prod, maybe limit to past 6 months.
            return db.query(Topic).all()

    def get_last_approved_category(self) -> str:
        """Fetches the category_type of the most recently approved topic."""
        with get_db_session() as db:
            last_topic = db.query(Topic).filter(Topic.is_approved == True).order_by(Topic.id.desc()).first()
            if last_topic and last_topic.category_type:
                return last_topic.category_type
            return "CURRENT_AFFAIRS" # Default if none found

    def save_topic(self, session_id: str, topic_data: Any, score_data: Any, is_approved: bool, category_type: str = "CURRENT_AFFAIRS") -> str:
        """Saves a topic and its score. Returns the topic ID."""
        with get_db_session() as db:
            db_topic = Topic(
                session_id=session_id,
                category_type=category_type,
                title=topic_data.title,
                problem_definition=topic_data.problem_definition,
                historical_comparison=topic_data.historical_comparison,
                root_cause_analysis=topic_data.root_cause_analysis,
                supporting_evidence=topic_data.supporting_evidence,
                counterarguments=topic_data.counterarguments,
                global_comparison=topic_data.global_comparison,
                practical_solutions=topic_data.practical_solutions,
                is_approved=is_approved,
                embedding=[0.1, 0.2, 0.3] # Mock embedding
            )
            db.add(db_topic)
            db.flush()
            
            db_score = TopicScore(
                topic_id=db_topic.id,
                evidence_strength=score_data.evidence_strength,
                source_reliability=score_data.source_reliability,
                historical_coverage=score_data.historical_coverage,
                expert_consensus=score_data.expert_consensus,
                conflict_risk=score_data.conflict_risk,
                educational_value=score_data.educational_value,
                practical_relevance=score_data.practical_relevance,
                total_score=score_data.total_score,
                confidence_score=score_data.confidence_score
            )
            db.add(db_score)
            
            return db_topic.id

    def complete_session(self, session_id: str, status: str = "COMPLETED") -> None:
        """Marks a research session as completed or failed."""
        from datetime import datetime
        with get_db_session() as db:
            session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
            if session:
                session.status = status
                session.ended_at = datetime.utcnow()
