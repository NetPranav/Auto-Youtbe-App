import json
import subprocess
from video_engine.models.state import Timeline
from common import logger



class AudioSynchronizer:
    def sync(self, timeline: Timeline) -> Timeline:
        logger.info("[AudioSynchronizer] Synchronizing visual duration with audio duration...")
        
        audio_clips = timeline.get_clips_by_type("AUDIO")
        if not audio_clips:
            logger.warning("[AudioSynchronizer] No audio clip found, skipping sync.")
            return timeline
            
        voice_clip = audio_clips[0]
        actual_duration = self._get_audio_duration(voice_clip.asset_path)
        
        if actual_duration <= 0:
            logger.warning("[AudioSynchronizer] Could not probe audio length. Using estimated.")
            return timeline
            
        logger.info(f"[AudioSynchronizer] Probed actual audio duration: {actual_duration}s")
        
        visual_clips = timeline.get_clips_by_type("VISUAL")
        if not visual_clips:
            return timeline
            
        total_estimated = sum(c.duration for c in visual_clips)
        
        if total_estimated == 0:
            return timeline
            
        # Scale all visual clips proportionally to match exact audio length
        scale_factor = actual_duration / total_estimated
        
        current_time = 0.0
        for clip in visual_clips:
            new_duration = clip.duration * scale_factor
            clip.start_time = current_time
            clip.end_time = current_time + new_duration
            clip.duration = new_duration
            current_time += new_duration
            
        # Update audio/subtitle end times
        voice_clip.end_time = actual_duration
        voice_clip.duration = actual_duration
        
        subtitle_clips = timeline.get_clips_by_type("SUBTITLE")
        for sub in subtitle_clips:
            sub.end_time = actual_duration
            sub.duration = actual_duration
            
        timeline.total_duration = actual_duration
        
        return timeline

    def _get_audio_duration(self, file_path: str) -> float:
        try:
            cmd = [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1", file_path
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
            logger.error(f"[AudioSynchronizer] ffprobe failed: {result.stderr}")
            return 0.0
        except Exception as e:
            logger.error(f"[AudioSynchronizer] Failed to get audio duration: {e}")
            return 0.0
