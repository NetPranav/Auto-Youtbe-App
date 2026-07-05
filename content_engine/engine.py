from typing import Any, Optional
from common import logger
from common.interfaces import BaseEngine
from config import config

from database.session import get_db_session
from database.models import Topic

from .models import ContentPackageData, QualityScores
from .research_context.builder import ResearchContextBuilder
from .content_strategy.strategist import ContentStrategist
from .hook_generator.generator import HookGenerator
from .outline_generator.generator import OutlineGenerator
from .script_generator.generator import ScriptGenerator
from .fact_checker.checker import FactChecker
from .script_reviewer.reviewer import ScriptReviewer
from .retention_analyzer.analyzer import RetentionAnalyzer
from .script_optimizer.optimizer import ScriptOptimizer
from .scene_planner.planner import ScenePlanner
from .content_repository.repository import ContentRepository

class ContentEngine(BaseEngine):
    """
    Facade for the Content Phase (AI Writers' Room).
    """
    def __init__(self, db_session: Any = None, provider_manager: Any = None):
        self.db_session = db_session
        self.provider_manager = provider_manager
        
        if not provider_manager:
            from providers.manager import ProviderManager
            provider_manager = ProviderManager()
            self.provider_manager = provider_manager
            
        self.ai = provider_manager.get_llm_provider()
        self.repo = ContentRepository()
        
        self.context_builder = ResearchContextBuilder()
        self.strategist = ContentStrategist(self.ai)
        self.hook_generator = HookGenerator(self.ai)
        self.outline_generator = OutlineGenerator(self.ai)
        self.script_generator = ScriptGenerator(self.provider_manager, self.db_session)
        self.fact_checker = FactChecker(self.ai)
        self.script_reviewer = ScriptReviewer(self.ai)
        self.retention_analyzer = RetentionAnalyzer(self.ai)
        self.script_optimizer = ScriptOptimizer(self.ai)
        self.scene_planner = ScenePlanner(self.ai)

    def run(self, topic_id: str) -> Optional[ContentPackageData]:
        """
        Executes the content pipeline.
        """
        logger.info(f"=== Starting Content Engine for Topic {topic_id} ===")
        
        # 1. Load Topic from DB
        with get_db_session() as db:
            topic = db.query(Topic).filter(Topic.id == topic_id).first()
            if not topic:
                logger.error(f"Topic {topic_id} not found.")
                return None
            # Eagerly extract needed properties into a dict or build context here to avoid DetachedInstanceError
            context_doc = self.context_builder.build_context(topic)
        
        package_id = self.repo.create_package(topic_id)
        
        try:
            # 2. Context & Strategy
            strategy = self.strategist.generate_strategy(context_doc)
            
            # 3. Hook & Outline
            best_hook = self.hook_generator.generate_hook(context_doc, strategy)
            self.repo.save_hooks(package_id, [], best_hook)
            
            outline = self.outline_generator.generate_outline(context_doc, strategy)
            self.repo.save_outline(package_id, outline)
            
            # 4. First Draft
            current_script = self.script_generator.generate_draft(context_doc, strategy, best_hook, outline)
            script_id = self.repo.create_script(package_id)
            
            # 5. Optimization Loop
            max_loops = config.content_max_optimization_loops
            loop_count = 0
            final_scores = QualityScores()
            
            while loop_count < max_loops:
                loop_count += 1
                logger.info(f"--- Optimization Loop {loop_count}/{max_loops} ---")
                
                # Review
                fact_res = self.fact_checker.check(current_script)
                rev_res = self.script_reviewer.review(current_script)
                ret_res = self.retention_analyzer.analyze(current_script)
                
                final_scores.fact_score = fact_res["fact_score"]
                final_scores.script_quality_score = rev_res["script_quality_score"]
                final_scores.retention_score = ret_res["retention_score"]
                
                feedback_notes = fact_res["feedback_notes"] + rev_res["feedback_notes"] + ret_res["feedback_notes"]
                final_scores.feedback_notes = feedback_notes
                
                # Save Revision
                feedback_dict = {
                    "fact_score": final_scores.fact_score,
                    "retention_score": final_scores.retention_score,
                    "quality_score": final_scores.script_quality_score,
                    "notes": feedback_notes
                }
                self.repo.add_revision(script_id, loop_count, current_script, feedback_dict)
                
                # Check Gates
                if (final_scores.fact_score >= config.content_min_fact_score and 
                    final_scores.retention_score >= config.content_min_retention_score):
                    logger.info("Quality gates passed!")
                    break
                    
                if loop_count < max_loops:
                    current_script = self.script_optimizer.optimize(current_script, feedback_dict)
                else:
                    logger.warning("Max optimization loops reached. Proceeding with best version.")
            
            # Save final scores
            self.repo.update_script_scores(script_id, final_scores.fact_score, final_scores.retention_score, final_scores.script_quality_score)
            
            # 6. Scene Planning
            scenes = self.scene_planner.plan_scenes(current_script)
            self.repo.save_scenes(package_id, scenes)
            
            self.repo.complete_package(package_id, "FINALIZED")
            logger.info("=== Content Engine Completed Successfully ===")
            
            # Return In-Memory Package
            return ContentPackageData(
                topic_id=topic_id,
                strategy=strategy,
                winning_hook=best_hook,
                outline=outline,
                final_script=current_script,
                scene_timeline=scenes,
                scores=final_scores
            )
            
        except Exception as e:
            logger.error(f"Content Engine Failed: {e}", exc_info=True)
            self.repo.complete_package(package_id, "FAILED")
            return None
