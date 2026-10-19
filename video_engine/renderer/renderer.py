import os
import subprocess
import time
from typing import Optional, List
from video_engine.models.state import Timeline, TimelineClip
from common import logger

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception as e:
    logger.warning(f"Failed to load imageio_ffmpeg, falling back to system ffmpeg: {e}")
    FFMPEG_EXE = "ffmpeg"



class VideoRenderer:
    def __init__(self, output_dir: str = "assets/renders"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def render(self, timeline: Timeline, file_name: str) -> Optional[str]:
        logger.info(f"[VideoRenderer] Generating cinematic video (Duration: {timeline.total_duration}s)...")
        
        output_path = os.path.join(self.output_dir, file_name)
        
        visual_clips = timeline.get_clips_by_type("VISUAL")
        audio_clips = timeline.get_clips_by_type("AUDIO")
        
        if not visual_clips:
            logger.error("Cannot render without visual clips.")
            return None
        
        # If only 1 image, use simple Ken Burns on the single image
        if len(visual_clips) == 1:
            return self._render_single_image(visual_clips[0], audio_clips, timeline, output_path)
        
        # Multiple images: Ken Burns on each + crossfade transitions
        return self._render_multi_image(visual_clips, audio_clips, timeline, output_path)
    
    def _render_single_image(self, clip: TimelineClip, audio_clips: List[TimelineClip], 
                              timeline: Timeline, output_path: str) -> Optional[str]:
        """Renders a single image with Ken Burns zoom effect."""
        res_w, res_h = timeline.resolution.split("x")
        duration = max(clip.duration, 5.0)
        
        # Ken Burns: slow zoom from 100% to 120% over the clip duration
        # zoompan: z='min(zoom+0.0015,1.2)' starts at 1.0 and slowly zooms to 1.2x
        fps = timeline.fps
        total_frames = int(duration * fps)
        
        cmd = [FFMPEG_EXE, "-y", "-loop", "1", "-i", os.path.abspath(clip.asset_path)]
        
        if audio_clips:
            cmd.extend(["-i", audio_clips[0].asset_path])
        
        subtitle_clips = timeline.get_clips_by_type("SUBTITLE")
        
        # Build zoompan filter for Ken Burns effect
        filter_str = (
            f"scale=8000:-1,"  # Scale up for smooth zoompan
            f"zoompan=z='min(zoom+0.0008,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={total_frames}:s={res_w}x{res_h}:fps={fps},"
            f"format=yuv420p"
        )
        
        if subtitle_clips:
            drawtext_filters = self._build_drawtext_filters(subtitle_clips[0].asset_path, timeline)
            if drawtext_filters:
                filter_str += f",{drawtext_filters}"
        
        cmd.extend(["-vf", filter_str, "-c:v", "libx264", "-r", str(fps), "-pix_fmt", "yuv420p"])
        
        if audio_clips:
            cmd.extend(["-c:a", "aac", "-shortest"])
        else:
            cmd.extend(["-t", str(duration)])
            
        cmd.append(output_path)
        return self._execute_ffmpeg(cmd, output_path)
    
    def _render_multi_image(self, visual_clips: List[TimelineClip], audio_clips: List[TimelineClip],
                             timeline: Timeline, output_path: str) -> Optional[str]:
        """Renders multiple images with Ken Burns effects and crossfade transitions."""
        subtitle_clips = timeline.get_clips_by_type("SUBTITLE")
        res_w, res_h = timeline.resolution.split("x")
        fps = timeline.fps
        crossfade_duration = 0.5  # 0.5 second crossfade between scenes
        
        # Step 1: Generate individual Ken Burns clips for each image
        temp_clips = []
        for i, clip in enumerate(visual_clips):
            temp_path = os.path.join(self.output_dir, f"_temp_clip_{i}.mp4")
            duration = max(clip.duration, 2.0)
            total_frames = int(duration * fps)
            
            # Use the motion_type assigned by MotionEngine (falls back to zoom_in)
            motion = getattr(clip, 'motion_type', 'zoom_in') or 'zoom_in'
            intensity = getattr(clip, 'motion_intensity', 1.15) or 1.15
            
            # Convert motion_type to FFmpeg zoompan parameters
            zoom_speed = (intensity - 1.0) / max(total_frames, 1)
            
            if motion == "zoom_in":
                zoompan = f"z='min(zoom+{zoom_speed:.6f},{intensity})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            elif motion == "zoom_out":
                zoompan = f"z='if(eq(on,1),{intensity},max(zoom-{zoom_speed:.6f},1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            elif motion == "pan_right":
                zoompan = f"z='{min(intensity, 1.15)}':x='min(x+2,iw)':y='ih/2-(ih/zoom/2)'"
            elif motion == "pan_left":
                zoompan = f"z='{min(intensity, 1.15)}':x='max(x-2,0)':y='ih/2-(ih/zoom/2)'"
            elif motion == "static":
                # No motion — hold still at 1.0x zoom, centred
                zoompan = f"z='1.0':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            else:
                # Fallback: gentle zoom in
                zoompan = f"z='min(zoom+0.001,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            
            filter_str = (
                f"scale=8000:-1,"
                f"zoompan={zoompan}:d={total_frames}:s={res_w}x{res_h}:fps={fps},"
                f"format=yuv420p"
            )
            
            cmd = [
                FFMPEG_EXE, "-y", "-loop", "1",
                "-i", os.path.abspath(clip.asset_path),
                "-vf", filter_str,
                "-c:v", "libx264", "-r", str(fps),
                "-pix_fmt", "yuv420p",
                "-t", str(duration),
                temp_path
            ]
            
            logger.info(f"[VideoRenderer] Rendering scene {i+1}/{len(visual_clips)} ({motion})...")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                logger.error(f"[VideoRenderer] Failed to render scene {i+1}: {result.stderr[-200:]}")
                continue
            temp_clips.append(temp_path)
        
        if not temp_clips:
            logger.error("[VideoRenderer] No temp clips were rendered successfully.")
            return None
        
        # Step 2: Concatenate with crossfade transitions
        if len(temp_clips) == 1:
            # Only one clip succeeded, just use it
            final_video_no_audio = temp_clips[0]
        else:
            final_video_no_audio = os.path.join(self.output_dir, "_temp_merged.mp4")
            
            # Build xfade filter chain
            cmd = [FFMPEG_EXE, "-y"]
            for clip_path in temp_clips:
                cmd.extend(["-i", clip_path])
            
            # Build the xfade filtergraph
            # [0][1]xfade=transition=fade:duration=0.5:offset=X[v01]; [v01][2]xfade=...
            filter_parts = []
            current_offset = 0.0
            
            for i in range(len(temp_clips) - 1):
                # Get duration of current clip
                clip_duration = visual_clips[i].duration if i < len(visual_clips) else 3.0
                clip_duration = max(clip_duration, 2.0)
                
                current_offset += clip_duration - crossfade_duration
                
                if i == 0:
                    input_label = f"[0][1]"
                else:
                    input_label = f"[v{i-1}{i}][{i+1}]"
                
                output_label = f"[v{i}{i+1}]"
                
                # Alternate transition types
                transitions = ["fade", "fadeblack", "slideleft", "slideright"]
                transition = transitions[i % len(transitions)]
                
                filter_parts.append(
                    f"{input_label}xfade=transition={transition}:duration={crossfade_duration}:offset={current_offset}{output_label}"
                )
            
            filter_str = ";".join(filter_parts)
            
            # The final output label
            final_label = f"[v{len(temp_clips)-2}{len(temp_clips)-1}]"
            
            cmd.extend([
                "-filter_complex", filter_str,
                "-map", final_label,
                "-c:v", "libx264", "-r", str(fps),
                "-pix_fmt", "yuv420p",
                final_video_no_audio
            ])
            
            logger.info(f"[VideoRenderer] Merging {len(temp_clips)} clips with crossfade transitions...")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                logger.error(f"[VideoRenderer] Crossfade merge failed: {result.stderr[-300:]}")
                # Fallback: simple concat without transitions
                logger.warning("[VideoRenderer] Falling back to simple concatenation...")
                final_video_no_audio = self._simple_concat(temp_clips, timeline, output_path + ".tmp.mp4")
                if not final_video_no_audio:
                    return None
        
        # Step 3: Mux audio, BGM, and burn subtitles onto the merged video
        bgm_clips = timeline.get_clips_by_type("AUDIO_BGM")
        
        if audio_clips or subtitle_clips or bgm_clips:
            cmd = [FFMPEG_EXE, "-y", "-i", final_video_no_audio]
            
            input_idx = 1  # [0] is the video
            voice_idx = None
            bgm_idx = None
            
            if audio_clips:
                cmd.extend(["-i", audio_clips[0].asset_path])
                voice_idx = input_idx
                input_idx += 1
            
            if bgm_clips and os.path.exists(bgm_clips[0].asset_path):
                cmd.extend(["-i", bgm_clips[0].asset_path])
                bgm_idx = input_idx
                input_idx += 1
            
            # Build filter complex for audio mixing
            filter_parts = []
            
            # Subtitle drawtext filter (video filter)
            vf_str = None
            if subtitle_clips:
                drawtext_filters = self._build_drawtext_filters(subtitle_clips[0].asset_path, timeline)
                if drawtext_filters:
                    vf_str = drawtext_filters
            
            # Audio mixing filter
            if voice_idx is not None and bgm_idx is not None:
                # Mix voice + BGM with ducked volume
                bgm_volume = getattr(bgm_clips[0], 'volume', 0.1) or 0.1
                fade_in = getattr(bgm_clips[0], 'fade_in', 2.0) or 2.0
                fade_out = getattr(bgm_clips[0], 'fade_out', 3.0) or 3.0
                total_dur = timeline.total_duration
                
                af_parts = []
                af_parts.append(f"[{voice_idx}:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=mono[voice];")
                af_parts.append(
                    f"[{bgm_idx}:a]volume={bgm_volume},"
                    f"afade=t=in:st=0:d={fade_in},"
                    f"afade=t=out:st={max(0, total_dur - fade_out)}:d={fade_out},"
                    f"aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=mono[bgm];"
                )
                af_parts.append("[voice][bgm]amix=inputs=2:duration=shortest[aout]")
                
                filter_complex = "".join(af_parts)
                if vf_str:
                    cmd.extend(["-filter_complex", filter_complex, "-vf", vf_str])
                else:
                    cmd.extend(["-filter_complex", filter_complex])
                cmd.extend(["-map", "0:v", "-map", "[aout]", "-c:v", "libx264", "-c:a", "aac", "-shortest"])
                logger.info("[VideoRenderer] Mixing voice + BGM audio tracks...")
            elif voice_idx is not None:
                if vf_str:
                    cmd.extend(["-vf", vf_str])
                cmd.extend(["-c:v", "libx264", "-c:a", "aac", "-shortest"])
            else:
                if vf_str:
                    cmd.extend(["-vf", vf_str])
                cmd.extend(["-c:v", "libx264"])
                
            cmd.append(output_path)
            
            logger.info(f"[VideoRenderer] Muxing audio & burning subtitles onto final video...")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                logger.error(f"[VideoRenderer] Mux/Subtitle failed: {result.stderr[-300:]}")
                # Use video without audio/subs if failed
                os.rename(final_video_no_audio, output_path)
        else:
            os.rename(final_video_no_audio, output_path)
        
        # Cleanup temp files
        for f in temp_clips:
            if os.path.exists(f) and f != output_path:
                os.remove(f)
        merged_tmp = os.path.join(self.output_dir, "_temp_merged.mp4")
        if os.path.exists(merged_tmp):
            os.remove(merged_tmp)
            
        logger.info(f"[VideoRenderer] Successfully rendered cinematic video: {output_path}")
        return output_path
    
    def _build_drawtext_filters(self, srt_path: str, timeline: Timeline) -> Optional[str]:
        """Parses an SRT file and converts it to FFmpeg drawtext filters (bypassing libass)."""
        import re
        if not os.path.exists(srt_path):
            return None
            
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"[VideoRenderer] Failed to read SRT: {e}")
            return None
            
        # Match SRT blocks:
        # 1
        # 00:00:00,000 --> 00:00:02,000
        # Text
        blocks = re.split(r'\n\n+', content.strip())
        filters = []
        
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:
                # Parse times
                time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
                if not time_match:
                    continue
                    
                start_str, end_str = time_match.groups()
                
                # Convert to seconds
                def to_seconds(t_str):
                    h, m, s_ms = t_str.split(':')
                    s, ms = s_ms.split(',')
                    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0
                
                start_sec = to_seconds(start_str)
                end_sec = to_seconds(end_str)
                
                # Clean text
                text = " ".join(lines[2:])
                # Wrap text to ~15 chars to guarantee it never overflows width at large font sizes
                import textwrap
                wrapped = textwrap.wrap(text, width=15)
                # Join with literal \n (escaped for ffmpeg) or just standard newline depending on ffmpeg version.
                # Actually, drawtext supports vertical spacing via \n only if we use text='line1\nline2'.
                # We need to escape single quotes, colons, AND newlines for FFmpeg drawtext inline string.
                escaped_text = "\\n".join(wrapped).replace("'", "\u2019").replace(":", "\\:")
                
                # Drawtext filter for this subtitle
                res_w, res_h = timeline.resolution.split("x")
                # Scale font appropriately for vertical video
                font_size = int(int(res_w) / 14)  # 77px for 1080p, safe width
                
                # Add a stylish solid yellow/white TikTok style text
                f_str = (
                    f"drawtext=text='{escaped_text}':fontcolor=white:fontsize={font_size}:"
                    f"box=1:boxcolor=black@0.7:boxborderw=20:" # Stylish background box
                    f"borderw=3:bordercolor=black:"
                    f"x=(w-text_w)/2:y=(h-text_h)/2+200:" # Centered vertically but pushed down slightly
                    f"enable='between(t,{start_sec},{end_sec})'"
                )
                filters.append(f_str)
                
        if filters:
            return ",".join(filters)
        return None
    
    def _simple_concat(self, clip_paths: list, timeline: Timeline, output_path: str) -> Optional[str]:
        """Fallback: simple concat without transitions."""
        concat_file = os.path.join(self.output_dir, "_concat_list.txt")
        with open(concat_file, "w") as f:
            for path in clip_paths:
                f.write(f"file '{os.path.abspath(path)}'\n")
        
        cmd = [
            FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264", "-r", str(timeline.fps),
            "-pix_fmt", "yuv420p",
            output_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if os.path.exists(concat_file):
            os.remove(concat_file)
        if result.returncode != 0:
            logger.error(f"[VideoRenderer] Simple concat also failed: {result.stderr[-200:]}")
            return None
        return output_path
        
    def _execute_ffmpeg(self, cmd: list, output_path: str) -> Optional[str]:
        """Execute an FFmpeg command and return the output path on success."""
        logger.info(f"[VideoRenderer] Executing FFmpeg...")
        start_time = time.time()
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                logger.error(f"[VideoRenderer] FFmpeg Error: {result.stderr[-300:]}")
                return None
        except Exception as e:
            logger.error(f"[VideoRenderer] Failed to run FFmpeg: {e}")
            return None
            
        render_time = time.time() - start_time
        logger.info(f"[VideoRenderer] Successfully rendered video in {render_time:.2f}s: {output_path}")
        return output_path
