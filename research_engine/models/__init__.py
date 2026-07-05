"""
Models module.
"""
from .article import ArticleData
from .topic import TopicCandidate, TopicScoreData, RankedTopic

__all__ = ["ArticleData", "TopicCandidate", "TopicScoreData", "RankedTopic"]
