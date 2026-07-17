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
        
        # Split script into paragraphs for simple heuristic scenes
        paragraphs = [p.strip() for p in script.split('\n\n') if p.strip()]
        if not paragraphs:
            paragraphs = ["Did you know this tech exists?"]
            
        scenes = []
        for i, para in enumerate(paragraphs):
            # Generate a simple visual description based on the paragraph
            words = para.split()
            keywords = " ".join(words[:10]) # use first few words as prompt
            
            scenes.append(
                SceneData(
                    scene_number=i+1,
                    start_time=f"00:0{i*5}", # mock times, AudioSync corrects this later anyway
                    end_time=f"00:0{(i+1)*5}",
                    narration_text=para,
                    visual_description=f"A cinematic representation of: {keywords}...",
                    animation_suggestions="Zoom in" if i % 2 == 0 else "Pan right",
                    asset_type_required="IMAGE",
                    transition_suggestion="Fade",
                    camera_movement="None",
                    subtitle_segment=para
                )
            )
        
        return scenes
