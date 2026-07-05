from typing import Any, List
from common import logger
from database.models import Scene

class AssetAnalyzer:
    """
    Reads every scene and determines what visual/audio assets are required.
    Does not generate anything, just lists the requirements.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def analyze(self, scenes: List[Scene]) -> List[dict]:
        """
        Returns a list of dicts describing required assets for each scene.
        """
        logger.info(f"Analyzing {len(scenes)} scenes for asset requirements...")
        
        requirements = []
        for scene in scenes:
            scene_reqs = {
                "scene_id": scene.id,
                "needs_voice": True, # Always need narration
                "needs_subtitle": True, # Always need subtitle
                "visuals": []
            }
            
            # Simple heuristic based on asset_type_required
            asset_type = (scene.asset_type_required or "").upper()
            if asset_type == "IMAGE":
                # Decide if it's an AI image or fetched logo based on visual description
                desc = scene.visual_description.lower() if scene.visual_description else ""
                if "logo" in desc or "icon" in desc:
                    scene_reqs["visuals"].append({"type": "FETCHED_IMAGE", "query": desc})
                else:
                    scene_reqs["visuals"].append({"type": "AI_IMAGE", "query": desc})
            elif asset_type == "VIDEO":
                scene_reqs["visuals"].append({"type": "STOCK_VIDEO", "query": scene.visual_description})
                
            requirements.append(scene_reqs)
            
        return requirements
