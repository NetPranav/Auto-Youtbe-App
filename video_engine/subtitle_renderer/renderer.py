import os
import uuid
from video_engine.models.state import Timeline
from common.logger import get_logger

logger = get_logger(__name__)

class SubtitleRenderer:
    def __init__(self, storage_dir: str = "assets/rendered"):
        self.storage_dir = storage_dir
        
    def process_subtitles(self, timeline: Timeline) -> Timeline:
        logger.info("[SubtitleRenderer] Converting SRT to ASS for high-quality styled rendering...")
        
        os.makedirs(self.storage_dir, exist_ok=True)
        
        subtitle_clips = timeline.get_clips_by_type("SUBTITLE")
        for clip in subtitle_clips:
            srt_path = clip.asset_path
            
            # Since FFmpeg uses libass to render subtitles, we will generate an ASS file
            # or just rely on FFmpeg's `subtitles=file.srt:force_style='FontName=Arial,FontSize=24'`
            # It's easier and cleaner to construct the FFmpeg filter string directly here.
            
            # We don't physically change the file, we just append the exact styling to the clip's properties.
            if not clip.properties_json:
                clip.properties_json = {}
                
            clip.properties_json["subtitle_style"] = (
                "FontName=Arial,"
                "FontSize=22,"
                "PrimaryColour=&H00FFFFFF,"
                "OutlineColour=&H00000000,"
                "BorderStyle=1,"
                "Outline=2,"
                "Shadow=1,"
                "MarginV=50"
            )
            
            logger.debug(f"[SubtitleRenderer] Styled subtitle clip {clip.id}")
            
        return timeline
