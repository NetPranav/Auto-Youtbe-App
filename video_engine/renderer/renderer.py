import os
import subprocess
import time
from typing import Optional
from video_engine.models.state import Timeline
from common.logger import get_logger

logger = get_logger(__name__)

class VideoRenderer:
    def __init__(self, output_dir: str = "assets/renders"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def render(self, timeline: Timeline, file_name: str) -> Optional[str]:
        logger.info(f"[VideoRenderer] Generating FFmpeg command for timeline (Duration: {timeline.total_duration}s)...")
        
        output_path = os.path.join(self.output_dir, file_name)
        
        # In a full production system, this generates a massive complex filtergraph:
        # e.g. [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=...
        # [1:v]scale... [0:v][1:v]xfade...
        
        visual_clips = timeline.get_clips_by_type("VISUAL")
        audio_clips = timeline.get_clips_by_type("AUDIO")
        subtitle_clips = timeline.get_clips_by_type("SUBTITLE")
        
        if not visual_clips:
            logger.error("Cannot render without visual clips.")
            return None
            
        # Simplified render process for this version:
        # 1. Create a text file with list of images/videos and their durations for ffmpeg concat demuxer
        concat_file = os.path.join(self.output_dir, f"concat_{file_name}.txt")
        with open(concat_file, "w", encoding="utf-8") as f:
            for clip in visual_clips:
                path = clip.asset_path.replace('\\', '/')
                f.write(f"file '{os.path.abspath(path)}'\n")
                f.write(f"duration {clip.duration}\n")
            # Ffmpeg requires repeating the last file without duration to avoid glitching
            if visual_clips:
                f.write(f"file '{os.path.abspath(visual_clips[-1].asset_path.replace('\\', '/'))}'\n")
                
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file
        ]
        
        # Add audio if present
        if audio_clips:
            voice = audio_clips[0].asset_path
            cmd.extend(["-i", voice])
            
        # Add basic formatting
        res = timeline.resolution.replace("x", ":")
        
        filter_str = f"scale={res}:force_original_aspect_ratio=increase,crop={res}"
        
        # Subtitles (simplified, assuming srt)
        if subtitle_clips:
            # Need to escape path for filter graph (replace \ with /, escape colons)
            sub_path = subtitle_clips[0].asset_path.replace('\\', '/').replace(':', '\\:')
            # Basic style string
            style = "FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1"
            filter_str += f",subtitles={sub_path}:force_style='{style}'"
            
        cmd.extend([
            "-vf", filter_str,
            "-c:v", "libx264",
            "-r", str(timeline.fps),
            "-pix_fmt", "yuv420p"
        ])
        
        if audio_clips:
            cmd.extend(["-c:a", "aac", "-shortest"])
            
        cmd.append(output_path)
        
        logger.info(f"[VideoRenderer] Executing FFmpeg:\n{' '.join(cmd)}")
        
        start_time = time.time()
        try:
            # Execute FFmpeg
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                logger.error(f"[VideoRenderer] FFmpeg Error: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"[VideoRenderer] Failed to run FFmpeg: {e}")
            return None
            
        render_time = time.time() - start_time
        logger.info(f"[VideoRenderer] Successfully rendered video in {render_time:.2f}s: {output_path}")
        
        # Cleanup concat
        if os.path.exists(concat_file):
            os.remove(concat_file)
            
        return output_path
