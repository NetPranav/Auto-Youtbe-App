import os
import json
from video_engine.models.state import Timeline
from database.models import VideoProject, Timeline as DBTimeline, RenderJob, RenderResult, VideoMetadata, RenderStatistics
from sqlalchemy.orm import Session
from common import logger



class VideoExporter:
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def export(self, project_id: str, timeline: Timeline, output_path: str, render_time: float) -> str:
        logger.info(f"[VideoExporter] Exporting final video package for project {project_id}...")
        
        project = self.db.query(VideoProject).filter(VideoProject.id == project_id).first()
        if not project:
            logger.error(f"Project {project_id} not found in DB.")
            return output_path
            
        project.status = "COMPLETED"
        
        # Save timeline state to DB
        db_timeline = DBTimeline(
            project_id=project_id,
            total_duration_sec=timeline.total_duration,
            timeline_json=timeline.dict()
        )
        self.db.add(db_timeline)
        self.db.commit()
        
        # Create Job and Result records
        job = RenderJob(
            project_id=project_id,
            timeline_id=db_timeline.id,
            status="SUCCESS"
        )
        self.db.add(job)
        self.db.commit()
        
        file_size = 0
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            
        result = RenderResult(
            job_id=job.id,
            output_path=output_path,
            file_size_bytes=file_size
        )
        self.db.add(result)
        self.db.commit()
        
        meta = VideoMetadata(
            result_id=result.id,
            resolution=timeline.resolution,
            fps=timeline.fps,
            codec="libx264",
            bitrate="5M"
        )
        stats = RenderStatistics(
            result_id=result.id,
            render_time_sec=render_time,
            hardware_accelerated=False
        )
        self.db.add_all([meta, stats])
        self.db.commit()
        
        logger.info(f"[VideoExporter] Export complete. Final MP4 ready at: {output_path}")
        return output_path
