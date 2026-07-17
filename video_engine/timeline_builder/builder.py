import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from common import logger
from database.models import AssetPackage, Asset, Scene
from video_engine.models.state import Timeline, TimelineClip



class TimelineBuilder:
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def build(self, project_id: str, asset_package_id: str, resolution: str = "1080x1920", fps: int = 30) -> Timeline:
        logger.info(f"[TimelineBuilder] Building timeline for Asset Package: {asset_package_id}")
        
        package = self.db.query(AssetPackage).filter(AssetPackage.id == asset_package_id).first()
        if not package:
            raise ValueError(f"AssetPackage {asset_package_id} not found")
            
        content_package = package.content_package_id
        scenes = self.db.query(Scene).filter(Scene.package_id == content_package).order_by(Scene.scene_number).all()
        
        timeline = Timeline(project_id=project_id, resolution=resolution, fps=fps)
        
        current_time = 0.0
        
        for scene in scenes:
            # We don't have exact durations yet, Audio Sync will fix durations.
            # For now, default to 3 seconds per scene, or guess based on narration length.
            estimated_duration = len(scene.narration_text.split()) / 2.5 # ~2.5 words per second
            if estimated_duration < 2.0:
                estimated_duration = 2.0
                
            # Find visual asset
            visual_asset = self.db.query(Asset).filter(
                Asset.package_id == asset_package_id,
                Asset.scene_id == scene.id,
                Asset.asset_type == "IMAGE" # Or video
            ).first()
            
            if visual_asset:
                clip = TimelineClip(
                    id=str(uuid.uuid4()),
                    scene_id=scene.id,
                    clip_type="VISUAL",
                    asset_path=visual_asset.file_path,
                    start_time=current_time,
                    end_time=current_time + estimated_duration,
                    duration=estimated_duration,
                    layer=0
                )
                timeline.clips.append(clip)
                
            current_time += estimated_duration
            
        # Add Voiceover and Subtitles
        voice_asset = self.db.query(Asset).filter(
            Asset.package_id == asset_package_id,
            Asset.asset_type == "VOICE"
        ).first()
        
        if voice_asset:
            # The duration will be updated in AudioSync module
            clip = TimelineClip(
                id=str(uuid.uuid4()),
                clip_type="AUDIO",
                asset_path=voice_asset.file_path,
                start_time=0.0,
                end_time=current_time,
                duration=current_time,
                layer=1
            )
            timeline.clips.append(clip)
            
        subtitle_asset = self.db.query(Asset).filter(
            Asset.package_id == asset_package_id,
            Asset.asset_type == "SUBTITLE"
        ).first()
        
        if subtitle_asset:
            clip = TimelineClip(
                id=str(uuid.uuid4()),
                clip_type="SUBTITLE",
                asset_path=subtitle_asset.file_path,
                start_time=0.0,
                end_time=current_time,
                duration=current_time,
                layer=2
            )
            timeline.clips.append(clip)
            
        timeline.total_duration = current_time
        return timeline
