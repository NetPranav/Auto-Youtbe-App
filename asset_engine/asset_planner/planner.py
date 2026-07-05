from typing import List, Dict, Any
from common import logger
from ..models import AssetRequest
from config import config

class AssetPlanner:
    """
    Creates an execution plan mapping abstract requirements to concrete providers.
    """
    def plan_assets(self, analyzed_scenes: List[Dict[str, Any]], script_text: str) -> List[AssetRequest]:
        logger.info("Planning asset execution strategy...")
        
        requests: List[AssetRequest] = []
        
        # 1. Global Assets (Voice, Subtitles)
        # We can map these to scene_id=None or the first scene. Let's use "global" as a marker
        requests.append(AssetRequest(
            scene_id="global",
            asset_type="VOICE",
            provider_type=config.voice_provider,
            parameters={"text": script_text, "style": config.asset_voice_style}
        ))
        
        requests.append(AssetRequest(
            scene_id="global",
            asset_type="SUBTITLE",
            provider_type="internal",
            parameters={"text": script_text}
        ))
        
        # 2. Scene-specific Visual Assets
        for req in analyzed_scenes:
            scene_id = req["scene_id"]
            for vis in req["visuals"]:
                if vis["type"] == "AI_IMAGE":
                    requests.append(AssetRequest(
                        scene_id=scene_id,
                        asset_type="IMAGE",
                        provider_type=config.image_provider,
                        parameters={"prompt": vis["query"]},
                        expected_dimensions=config.asset_output_resolution
                    ))
                elif vis["type"] == "FETCHED_IMAGE":
                    requests.append(AssetRequest(
                        scene_id=scene_id,
                        asset_type="FETCHED_IMAGE",
                        provider_type=config.stock_provider, 
                        parameters={"query": vis["query"]}
                    ))
                elif vis["type"] == "STOCK_VIDEO":
                    requests.append(AssetRequest(
                        scene_id=scene_id,
                        asset_type="STOCK_VIDEO",
                        provider_type=config.stock_provider,
                        parameters={"query": vis["query"]}
                    ))
                    
        logger.info(f"Generated plan for {len(requests)} total assets.")
        return requests
