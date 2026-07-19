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
        
        import re
        
        # Split script into sentences for high-paced, context-matched scenes
        # This splits by punctuation (., !, ?) followed by a space
        raw_sentences = re.split(r'(?<=[.!?]) +', script.replace('\n', ' '))
        sentences = [s.strip() for s in raw_sentences if s.strip()]
        
        if not sentences:
            sentences = ["Did you know this tech exists?"]
            
        scenes = []
        for i, sentence in enumerate(sentences):
            # Generate a simple visual description based on the sentence
            # Remove non-alphanumeric chars for cleaner prompting
            clean_sentence = re.sub(r'[^a-zA-Z0-9 ]', '', sentence)
            words = clean_sentence.split()
            keywords = " ".join(words[:7]) # use first few words as prompt
            
            # Alternate animations
            animations = ["Zoom in", "Pan right", "Zoom out", "Pan left"]
            animation = animations[i % len(animations)]
            
            scenes.append(
                SceneData(
                    scene_number=i+1,
                    start_time=f"00:0{i*5}", # mock times, AudioSync corrects this later anyway
                    end_time=f"00:0{(i+1)*5}",
                    narration_text=sentence,
                    visual_description=f"A cinematic, historical documentary scene of: {keywords}, hyper-realistic, dramatic lighting, 8k resolution",
                    animation_suggestions=animation,
                    asset_type_required="IMAGE",
                    transition_suggestion="Fade",
                    camera_movement="None",
                    subtitle_segment=sentence
                )
            )
        
        return scenes
