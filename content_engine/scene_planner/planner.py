from typing import Any, List
from common import logger
from ..models import SceneData

class ScenePlanner:
    """
    Converts the final script into a detailed chronological visual timeline.
    Does NOT generate assets, only descriptions.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def plan_scenes(self, script: str) -> List[SceneData]:
        """
        Generates the scene timeline.
        """
        logger.info("Planning scenes based on final script...")
        
        # Mock scene planning
        if self.ai:
            from providers.models import TaskCategory
            prompt = f"Plan scenes for this script: {script}"
            scenes_text = self.ai.generate_text(
                prompt=prompt, 
                system_prompt="You are a YouTube video director.",
                task_category=TaskCategory.CONTENT_SCENE_PLANNING
            )
            # In a real impl we'd parse JSON from the LLM to build scenes.
            # For now, we fallback to our basic regex matcher if it's mock text. 
        
        scenes = [
            SceneData(
                scene_number=1,
                start_time="00:00",
                end_time="00:05",
                narration_text="Did you know this tech exists?",
                visual_description="A dynamic text animation showing a question mark.",
                animation_suggestions="Zoom in",
                asset_type_required="IMAGE",
                transition_suggestion="Fade to black",
                camera_movement="None",
                subtitle_segment="Did you know this tech exists?"
            )
        ]
        
        return scenes
