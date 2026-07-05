import pytest
from unittest.mock import MagicMock
from research_engine.models import ArticleData, TopicCandidate
from research_engine.article_normalizer.normalizer import ArticleNormalizer
from research_engine.duplicate_detector.detector import DuplicateDetector
from research_engine.topic_ranker.ranker import TopicRanker
from research_engine.topic_selector.selector import TopicSelector
from research_engine.models.topic import RankedTopic, TopicScoreData
from database.models import Topic

def test_article_normalizer():
    normalizer = ArticleNormalizer()
    raw = ArticleData(
        title="  Test Title  ",
        url="https://example.com?utm_source=twitter&valid=true",
        source="Test",
        summary="<p>This is a <b>test</b>.</p>"
    )
    normalized = normalizer.normalize([raw])[0]
    
    assert normalized.title == "Test Title"
    assert "utm_source" not in normalized.url
    assert "valid=true" in normalized.url
    assert normalized.summary == "This is a test."

def test_duplicate_detector():
    detector = DuplicateDetector()
    candidate = TopicCandidate(
        title="New Topic",
        main_technology="Python",
        description="A new python topic."
    )
    
    past_topics = [Topic(title="New Topic")]
    assert detector.is_duplicate(candidate, past_topics) == True
    
    past_topics = [Topic(title="Different Topic")]
    assert detector.is_duplicate(candidate, past_topics) == False

def test_topic_ranker():
    ranker = TopicRanker()
    # Mocking some weights for test predictability
    ranker.weights = {
        "novelty": 1.0, "audience": 1.0, "educational": 1.0, 
        "recency": 1.0, "competition": 1.0, "search_interest": 1.0
    }
    
    candidate = TopicCandidate(
        title="Test", main_technology="Test", description="Test",
        estimated_audience="Mass"
    )
    
    score = ranker.rank(candidate, novelty_score=1.0)
    # 1.0 (novelty) + 1.0 (mass audience) + 0.8 (edu) + 0.9 (recency) + 0.4 (comp) + 0.6 (search)
    assert score.total_score == pytest.approx(4.7)

def test_topic_selector():
    selector = TopicSelector()
    selector.minimum_score = 3.0
    
    candidate = TopicCandidate(title="Winning Topic", main_technology="Test", description="Test")
    ranked1 = RankedTopic(topic_id="1", candidate=candidate, score=TopicScoreData(total_score=5.0))
    ranked2 = RankedTopic(topic_id="2", candidate=candidate, score=TopicScoreData(total_score=2.0))
    
    best = selector.select([ranked1, ranked2])
    assert best is not None
    assert best.score.total_score == 5.0
