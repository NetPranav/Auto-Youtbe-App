import os
import uuid
import random
from video_engine.models.state import Timeline, TimelineClip
from common import logger



class MusicMixer:
    def __init__(self, music_dir: str = "assets/music"):
        self.music_dir = music_dir
        
    def mix(self, timeline: Timeline) -> Timeline:
        logger.info("[MusicMixer] Selecting and mixing background music...")
        
        # Check if music dir exists and has files
        if not os.path.exists(self.music_dir):
            logger.warning(f"Music directory {self.music_dir} does not exist. Skipping BGM.")
            return timeline
            
        music_files = [f for f in os.listdir(self.music_dir) if f.endswith(".mp3")]
        if not music_files:
            logger.warning("No .mp3 files found in music directory. Skipping BGM.")
            return timeline
            
        selected_bgm = random.choice(music_files)
        bgm_path = os.path.join(self.music_dir, selected_bgm)
        
        bgm_clip = TimelineClip(
            id=str(uuid.uuid4()),
            clip_type="AUDIO_BGM",
            asset_path=bgm_path,
            start_time=0.0,
            end_time=timeline.total_duration,
            duration=timeline.total_duration,
            layer=2,
            volume=0.1, # Ducked volume
            fade_in=2.0,
            fade_out=3.0
        )
        
        timeline.clips.append(bgm_clip)
        logger.info(f"[MusicMixer] Added BGM {selected_bgm} to timeline.")
        return timeline
