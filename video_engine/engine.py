import uuid
import time
from sqlalchemy.orm import Session
from config import config
from common.logger import get_logger
from database.models import AssetPackage, VideoProject

from video_engine.timeline_builder.builder import TimelineBuilder
from video_engine.audio_sync.sync import AudioSynchronizer
from video_engine.asset_placement.placement import AssetPlacementEngine
from video_engine.motion_engine.motion import MotionEngine
from video_engine.transition_engine.transition import TransitionEngine
from video_engine.subtitle_renderer.renderer import SubtitleRenderer
from video_engine.music_engine.mixer import MusicMixer
from video_engine.effects_engine.effects import EffectsEngine
from video_engine.quality_validator.validator import QualityValidator
from video_engine.renderer.renderer import VideoRenderer
from video_engine.exporter.exporter import VideoExporter

logger = get_logger(__name__)

class VideoEngine:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.timeline_builder = TimelineBuilder(self.db)
        self.audio_sync = AudioSynchronizer()
        self.asset_placement = AssetPlacementEngine()
        self.motion_engine = MotionEngine()
        self.transition_engine = TransitionEngine()
        self.subtitle_renderer = SubtitleRenderer()
        self.music_mixer = MusicMixer()
        self.effects_engine = EffectsEngine()
        self.validator = QualityValidator()
        self.renderer = VideoRenderer()
        self.exporter = VideoExporter(self.db)
        
    def run(self, asset_package_id: str) -> str:
        logger.info(f"=== Starting Phase 5: Video Engine for Asset Package {asset_package_id} ===")
        
        # 1. Create Video Project
        project_id = str(uuid.uuid4())
        project = VideoProject(
            id=project_id,
            asset_package_id=asset_package_id,
            status="BUILDING_TIMELINE"
        )
        self.db.add(project)
        self.db.commit()
        
        res = config.asset_video_resolution
        fps = config.video_fps
        
        # 2. Timeline Builder
        timeline = self.timeline_builder.build(project_id, asset_package_id, res, fps)
        
        # 3. Audio Synchronization
        timeline = self.audio_sync.sync(timeline)
        
        # 4. Asset Placement
        timeline = self.asset_placement.place(timeline)
        
        # 5. Motion Engine
        timeline = self.motion_engine.apply_motion(timeline)
        
        # 6. Transition Engine
        timeline = self.transition_engine.apply_transitions(timeline)
        
        # 7. Subtitle Renderer
        timeline = self.subtitle_renderer.process_subtitles(timeline)
        
        # 8. Background Music Mixer
        timeline = self.music_mixer.mix(timeline)
        
        # 9. Effects Engine
        timeline = self.effects_engine.apply_effects(timeline)
        
        # 10. Quality Validation
        if not self.validator.validate(timeline):
            project.status = "FAILED"
            self.db.commit()
            raise ValueError("Video timeline failed quality validation")
            
        project.status = "RENDERING"
        self.db.commit()
        
        # 11. Render
        output_name = f"final_video_{project_id[:8]}.mp4"
        start_time = time.time()
        final_mp4_path = self.renderer.render(timeline, output_name)
        
        if not final_mp4_path:
            project.status = "FAILED"
            self.db.commit()
            raise RuntimeError("FFmpeg rendering failed")
            
        render_time = time.time() - start_time
        
        # 12. Exporter
        final_path = self.exporter.export(project_id, timeline, final_mp4_path, render_time)
        
        logger.info(f"=== Video Engine Completed Successfully ===")
        return final_path
