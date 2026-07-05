from typing import Any, Optional
from common import logger
from common.interfaces import BaseEngine
from config import config

from database.session import get_db_session
from database.models import ContentPackage, Scene, Script

from .models import AssetPackageData, AssetResult
from .asset_analyzer.analyzer import AssetAnalyzer
from .asset_planner.planner import AssetPlanner
from .image_generator.generator import ImageGenerator
from .asset_fetchers.fetcher import AssetFetcherManager
from .voice_generator.generator import VoiceGenerator
from .subtitle_generator.generator import SubtitleGenerator
from .asset_validator.validator import AssetValidator
from .asset_repository.repository import AssetRepository

class AssetEngine(BaseEngine):
    """
    Facade for the Asset Phase.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider
        self.repo = AssetRepository()
        
        self.analyzer = AssetAnalyzer(self.ai)
        self.planner = AssetPlanner()
        
        self.image_generator = ImageGenerator()
        self.asset_fetcher = AssetFetcherManager()
        self.voice_generator = VoiceGenerator()
        self.subtitle_generator = SubtitleGenerator()
        
        self.validator = AssetValidator()

    def run(self, content_package_id: str) -> Optional[AssetPackageData]:
        logger.info(f"=== Starting Asset Engine for Content Package {content_package_id} ===")
        
        pkg_id = self.repo.create_package(content_package_id)
        storage_dir = f"{config.asset_storage_dir}/{pkg_id}"
        
        try:
            with get_db_session() as db:
                c_pkg = db.query(ContentPackage).filter(ContentPackage.id == content_package_id).first()
                if not c_pkg:
                    logger.error("Content package not found.")
                    return None
                scenes = c_pkg.scenes
                script = db.query(Script).filter(Script.package_id == content_package_id).first()
                script_text = script.revisions[-1].text if script and script.revisions else "Default script text"
                
                # 1. Analyze & Plan inside session to avoid DetachedInstanceError
                analyzed_scenes = self.analyzer.analyze(scenes)
                plan = self.planner.plan_assets(analyzed_scenes, script_text)
            
            results = []
            
            # 2. Execute Generation & Fetching
            for req in plan:
                file_path = None
                if req.asset_type == "IMAGE":
                    file_path = self.image_generator.generate(req.provider_type, req.parameters.get("prompt", ""), storage_dir)
                elif req.asset_type in ["FETCHED_IMAGE", "STOCK_VIDEO"]:
                    file_path = self.asset_fetcher.fetch(req.provider_type, req.parameters.get("query", ""), storage_dir)
                elif req.asset_type == "VOICE":
                    file_path = self.voice_generator.generate(req.provider_type, req.parameters.get("text", ""), storage_dir)
                elif req.asset_type == "SUBTITLE":
                    file_path = self.subtitle_generator.generate(req.parameters.get("text", ""), storage_dir)
                
                if not file_path:
                    logger.warning(f"Failed to generate asset for req: {req.asset_type}")
                    continue
                    
                # 3. Validate
                val_res = self.validator.validate(file_path, req.asset_type)
                
                # 4. Save to Repository
                asset_id = self.repo.save_asset(pkg_id, req.scene_id, req.asset_type, req.provider_type, file_path)
                self.repo.save_validation(asset_id, val_res["status"], val_res["report"])
                
                results.append(AssetResult(
                    request=req,
                    file_path=file_path,
                    status=val_res["status"],
                    metadata=val_res["report"]
                ))
            
            self.repo.complete_package(pkg_id, "FINALIZED")
            logger.info("=== Asset Engine Completed Successfully ===")
            
            return AssetPackageData(content_package_id=content_package_id, assets=results)
            
        except Exception as e:
            logger.error(f"Asset Engine Failed: {e}", exc_info=True)
            self.repo.complete_package(pkg_id, "FAILED")
            return None
