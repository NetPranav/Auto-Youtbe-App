import uuid
from typing import List
from sqlalchemy.orm import Session
from common import logger
from providers.manager import ProviderManager
from database.models import PublishedVideo, AnalyticsSnapshot, PerformanceReport

from learning_engine.analytics_collector.collector import AnalyticsCollector
from learning_engine.performance_analyzer.analyzer import PerformanceAnalyzer
from learning_engine.retention_analyzer.analyzer import RetentionAnalyzer
from learning_engine.seo_analyzer.analyzer import SEOAnalyzer
from learning_engine.thumbnail_analyzer.analyzer import ThumbnailAnalyzer
from learning_engine.audience_analyzer.analyzer import AudienceAnalyzer
from learning_engine.strategy_generator.generator import StrategyGenerator
from learning_engine.knowledge_base.manager import KnowledgeManager



class LearningEngine:
    def __init__(self, db_session: Session, provider_manager: ProviderManager):
        self.db = db_session
        self.provider_manager = provider_manager
        
        self.collector = AnalyticsCollector()
        self.perf_analyzer = PerformanceAnalyzer(self.provider_manager)
        self.retention_analyzer = RetentionAnalyzer(self.provider_manager)
        self.seo_analyzer = SEOAnalyzer()
        self.thumb_analyzer = ThumbnailAnalyzer()
        self.aud_analyzer = AudienceAnalyzer()
        
        self.strategy_generator = StrategyGenerator()
        self.knowledge_manager = KnowledgeManager(self.db)
        
    def run(self):
        logger.info("=== Starting Phase 7: Learning Intelligence Engine ===")
        
        # 1. Fetch published videos that haven't been analyzed recently
        # For simplicity, we just grab all videos that were published successfully
        published_videos = self.db.query(PublishedVideo).filter(PublishedVideo.status == "PUBLISHED").all()
        
        if not published_videos:
            logger.info("[LearningEngine] No published videos found to analyze.")
            return
            
        for video in published_videos:
            # Check if we have a platform video ID in the result
            if not video.result or not video.result.platform_video_id:
                continue
                
            platform_id = video.result.platform_video_id
            
            # 2. Collect Analytics
            metrics = self.collector.collect(platform_id)
            
            snapshot = AnalyticsSnapshot(
                id=str(uuid.uuid4()),
                published_video_id=video.id,
                views=metrics["views"],
                ctr_percent=metrics["ctr_percent"],
                avg_view_duration_sec=metrics["avg_view_duration_sec"],
                retention_graph_json=metrics["retention_graph"]
            )
            self.db.add(snapshot)
            self.db.commit()
            
            # 3. Analyze
            perf_findings = self.perf_analyzer.analyze(metrics)
            ret_findings = self.retention_analyzer.analyze(metrics["retention_graph"])
            seo_findings = self.seo_analyzer.analyze(metrics["ctr_percent"])
            thumb_findings = self.thumb_analyzer.analyze(metrics["ctr_percent"])
            aud_findings = self.aud_analyzer.analyze(metrics["views"])
            
            # Combine findings
            all_findings = {
                "performance": perf_findings,
                "retention": ret_findings,
                "seo": seo_findings,
                "thumbnail": thumb_findings,
                "audience": aud_findings
            }
            
            report = PerformanceReport(
                id=str(uuid.uuid4()),
                published_video_id=video.id,
                overall_score=perf_findings.get("overall_score", 0),
                findings_json=all_findings
            )
            self.db.add(report)
            self.db.commit()
            
            # 4. Generate Strategy
            recs = self.strategy_generator.generate(
                perf_findings, ret_findings, seo_findings, thumb_findings, aud_findings
            )
            
            # 5. Store Knowledge & Update Memory
            self.knowledge_manager.save_recommendations(report.id, recs)
            
        # Compile final global strategy
        self.knowledge_manager.compile_strategy_json()
        logger.info("=== Learning Intelligence Engine Completed Successfully ===")
