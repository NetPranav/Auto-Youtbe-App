import uuid
from typing import Optional, Dict
from sqlalchemy.orm import Session

from config import config
from common.logger import get_logger
from database.models import VideoProject, RenderResult, PublishedVideo, PlatformMetadata, UploadAttempt, PublishingSchedule, PublishingResult
from providers.manager import ProviderManager

from publisher.metadata_generator.generator import MetadataGenerator
from publisher.seo_optimizer.optimizer import SEOOptimizer
from publisher.thumbnail_selector.selector import ThumbnailSelector
from publisher.schedule_optimizer.optimizer import ScheduleOptimizer
from publisher.upload_validator.validator import UploadValidator
from publisher.notification_engine.notifier import NotificationEngine
from publisher.providers.youtube_publisher import YouTubePublisher

logger = get_logger(__name__)

class PublishingEngine:
    def __init__(self, db_session: Session, provider_manager: ProviderManager):
        self.db = db_session
        self.provider_manager = provider_manager
        
        self.metadata_generator = MetadataGenerator(self.provider_manager)
        self.seo_optimizer = SEOOptimizer()
        self.thumbnail_selector = ThumbnailSelector(self.db)
        self.schedule_optimizer = ScheduleOptimizer()
        self.upload_validator = UploadValidator()
        self.notification_engine = NotificationEngine(self.db)
        
        # Initialize platform publisher
        self.youtube_publisher = YouTubePublisher(config.youtube_client_secret_path)
        
    def run(self, project_id: str) -> Optional[str]:
        logger.info(f"=== Starting Phase 6: Publishing Engine for Project {project_id} ===")
        
        # 1. Fetch Video Package
        project = self.db.query(VideoProject).filter(VideoProject.id == project_id).first()
        if not project or project.status != "COMPLETED":
            logger.error("Invalid or incomplete Video Project.")
            return None
            
        render_job = project.render_jobs[-1] if project.render_jobs else None
        if not render_job or not render_job.result:
            logger.error("No Render Result found.")
            return None
            
        video_path = render_job.result.output_path
        
        # 2. Setup Publishing Record
        published_video = PublishedVideo(
            id=str(uuid.uuid4()),
            project_id=project.id,
            platform="YOUTUBE",
            status="PREPARING"
        )
        self.db.add(published_video)
        self.db.commit()
        
        # 3. Generate & Optimize Metadata
        # Find the script for context
        content_pkg = project.asset_package.content_package
        script_text = content_pkg.script_text if content_pkg else ""
        
        raw_metadata = self.metadata_generator.generate(script_text)
        optimized_metadata = self.seo_optimizer.optimize(raw_metadata)
        
        platform_meta = PlatformMetadata(
            published_video_id=published_video.id,
            title=optimized_metadata.get("title", ""),
            description=optimized_metadata.get("description", ""),
            tags_json=optimized_metadata.get("tags", []),
            category_id=config.youtube_default_category_id,
            visibility=config.youtube_default_visibility
        )
        self.db.add(platform_meta)
        
        # 4. Thumbnail Selection
        thumbnail_path = self.thumbnail_selector.select(project.asset_package_id)
        
        # 5. Validation
        if not self.upload_validator.validate(video_path, thumbnail_path, optimized_metadata):
            published_video.status = "FAILED"
            self.db.commit()
            self.notification_engine.notify("UPLOAD_FAILED", f"Validation failed for project {project_id}", "ERROR")
            return None
            
        # 6. Scheduling
        scheduled_time = self.schedule_optimizer.optimize(immediate=True)
        schedule_record = PublishingSchedule(
            published_video_id=published_video.id,
            scheduled_for=scheduled_time if scheduled_time else datetime.now(timezone.utc),
            is_published=False
        )
        self.db.add(schedule_record)
        self.db.commit()
        
        # 7. Uploading (with retries)
        published_video.status = "UPLOADING"
        self.db.commit()
        
        attempt_number = 1
        platform_video_id = None
        
        while attempt_number <= config.publishing_max_retries:
            logger.info(f"[PublishingEngine] Upload attempt {attempt_number}...")
            attempt = UploadAttempt(
                published_video_id=published_video.id,
                attempt_number=attempt_number,
                status="IN_PROGRESS"
            )
            self.db.add(attempt)
            self.db.commit()
            
            platform_video_id = self.youtube_publisher.upload_video(
                video_path=video_path,
                title=platform_meta.title,
                description=platform_meta.description,
                tags=platform_meta.tags_json,
                category_id=platform_meta.category_id,
                visibility=platform_meta.visibility,
                scheduled_time=scheduled_time
            )
            
            if platform_video_id:
                attempt.status = "SUCCESS"
                attempt.ended_at = datetime.now(timezone.utc)
                self.db.commit()
                break
                
            attempt.status = "FAILED"
            attempt.error_message = "YouTube API upload failed."
            attempt.ended_at = datetime.now(timezone.utc)
            self.db.commit()
            attempt_number += 1
            
        if not platform_video_id:
            published_video.status = "FAILED"
            self.db.commit()
            self.notification_engine.notify("UPLOAD_FAILED", f"All upload attempts failed for {project_id}", "ERROR")
            return None
            
        # 8. Upload Thumbnail
        if thumbnail_path:
            self.youtube_publisher.upload_thumbnail(platform_video_id, thumbnail_path)
            
        # 9. Verification & Result Storage
        published_video.status = "PUBLISHED"
        schedule_record.is_published = True
        
        url = f"https://www.youtube.com/watch?v={platform_video_id}"
        result = PublishingResult(
            published_video_id=published_video.id,
            platform_video_id=platform_video_id,
            platform_url=url,
            thumbnail_url=thumbnail_path
        )
        self.db.add(result)
        self.db.commit()
        
        self.notification_engine.notify("UPLOAD_SUCCESS", f"Video published successfully: {url}", "INFO")
        logger.info(f"=== Publishing Engine Completed Successfully. URL: {url} ===")
        
        return url

# Required for datetime timezone usage above
from datetime import datetime, timezone
