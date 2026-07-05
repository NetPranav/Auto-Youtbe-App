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

    def save_topic(self, session_id: str, topic_data: Any, score_data: Any, is_approved: bool) -> str:
        """Saves a topic and its score. Returns the topic ID."""
        with get_db_session() as db:
            db_topic = Topic(
                session_id=session_id,
                title=topic_data.title,
                main_technology=topic_data.main_technology,
                secondary_technologies=topic_data.secondary_technologies,
                industry=topic_data.industry,
                importance=topic_data.importance,
                estimated_audience=topic_data.estimated_audience,
                description=topic_data.description,
                is_approved=is_approved,
                embedding=[0.1, 0.2, 0.3] # Mock embedding
            )
            db.add(db_topic)
            db.flush()
            
            db_score = TopicScore(
                topic_id=db_topic.id,
                novelty=score_data.novelty,
                audience_size=score_data.audience_size,
                educational_value=score_data.educational_value,
                search_interest=score_data.search_interest,
                competition=score_data.competition,
                recency=score_data.recency,
                total_score=score_data.total_score
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
