from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from .base import Base

def generate_uuid():
    return str(uuid.uuid4())

class ResearchSession(Base):
    __tablename__ = 'research_sessions'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="IN_PROGRESS")  # IN_PROGRESS, COMPLETED, FAILED
    
    # Relationships
    sources = relationship("ProcessedSource", back_populates="session", cascade="all, delete-orphan")
    articles = relationship("Article", back_populates="session", cascade="all, delete-orphan")
    topics = relationship("Topic", back_populates="session", cascade="all, delete-orphan")

class ProcessedSource(Base):
    __tablename__ = 'processed_sources'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey('research_sessions.id'))
    source_name = Column(String(100), nullable=False)
    articles_found = Column(Integer, default=0)
    errors = Column(Text, nullable=True)
    
    session = relationship("ResearchSession", back_populates="sources")

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey('research_sessions.id'))
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    source = Column(String(100), nullable=False)
    publication_date = Column(DateTime, nullable=True)
    author = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    categories = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    
    session = relationship("ResearchSession", back_populates="articles")

class Topic(Base):
    __tablename__ = 'topics'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey('research_sessions.id'))
    title = Column(String(500), nullable=False)
    main_technology = Column(String(200))
    secondary_technologies = Column(JSON, nullable=True)
    industry = Column(String(200), nullable=True)
    importance = Column(String(50), nullable=True)  # Breaking, Major, Minor
    estimated_audience = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=False)
    embedding = Column(JSON, nullable=True) # Storing vector as JSON array for SQLite compatibility
    
    session = relationship("ResearchSession", back_populates="topics")
    score = relationship("TopicScore", back_populates="topic", uselist=False, cascade="all, delete-orphan")

class TopicScore(Base):
    __tablename__ = 'topic_scores'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    topic_id = Column(String(36), ForeignKey('topics.id'))
    novelty = Column(Float, default=0.0)
    audience_size = Column(Float, default=0.0)
    educational_value = Column(Float, default=0.0)
    search_interest = Column(Float, default=0.0)
    competition = Column(Float, default=0.0)
    recency = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0)
    
    topic = relationship("Topic", back_populates="score")

class ContentPackage(Base):
    __tablename__ = 'content_packages'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    topic_id = Column(String(36), ForeignKey('topics.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="DRAFTING")  # DRAFTING, REVISING, FINALIZED
    
    # Relationships
    script = relationship("Script", back_populates="package", uselist=False, cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="package", cascade="all, delete-orphan")

class Hook(Base):
    __tablename__ = 'hooks'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    package_id = Column(String(36), ForeignKey('content_packages.id'))
    text = Column(Text, nullable=False)
    score = Column(Float, default=0.0)
    is_selected = Column(Boolean, default=False)

class Outline(Base):
    __tablename__ = 'outlines'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    package_id = Column(String(36), ForeignKey('content_packages.id'))
    structure_json = Column(JSON, nullable=False)

class Script(Base):
    __tablename__ = 'scripts'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    package_id = Column(String(36), ForeignKey('content_packages.id'))
    fact_score = Column(Float, nullable=True)
    retention_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    
    package = relationship("ContentPackage", back_populates="script")
    revisions = relationship("ScriptRevision", back_populates="script", cascade="all, delete-orphan", order_by="ScriptRevision.iteration")

class ScriptRevision(Base):
    __tablename__ = 'script_revisions'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    script_id = Column(String(36), ForeignKey('scripts.id'))
    iteration = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    feedback_json = Column(JSON, nullable=True)
    
    script = relationship("Script", back_populates="revisions")

class Scene(Base):
    __tablename__ = 'scenes'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    package_id = Column(String(36), ForeignKey('content_packages.id'))
    scene_number = Column(Integer, nullable=False)
    narration_text = Column(Text, nullable=False)
    visual_description = Column(Text, nullable=True)
    asset_type_required = Column(String(100), nullable=True) # IMAGE, VIDEO, NONE
    
    package = relationship("ContentPackage", back_populates="scenes")

class AssetPackage(Base):
    __tablename__ = 'asset_packages'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    content_package_id = Column(String(36), ForeignKey('content_packages.id'))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(50), default="PROCESSING")  # PROCESSING, FINALIZED, FAILED
    
    assets = relationship("Asset", back_populates="package", cascade="all, delete-orphan")

class ProviderStatistic(Base):
    __tablename__ = 'provider_statistics'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_name = Column(String(50))
    model_used = Column(String(100))
    request_type = Column(String(50)) # e.g. 'generate_text', 'generate_image'
    task_category = Column(String(50)) # from TaskCategory enum
    execution_time_ms = Column(Float)
    success = Column(Boolean, default=True)
    tokens_used = Column(Integer, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class VideoProject(Base):
    __tablename__ = 'video_projects'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    asset_package_id = Column(String(36), ForeignKey('asset_packages.id'))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(50), default="BUILDING_TIMELINE") # BUILDING_TIMELINE, RENDERING, COMPLETED, FAILED
    
    asset_package = relationship("AssetPackage")
    timelines = relationship("Timeline", back_populates="project", cascade="all, delete-orphan")
    render_jobs = relationship("RenderJob", back_populates="project", cascade="all, delete-orphan")

class Timeline(Base):
    __tablename__ = 'timelines'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey('video_projects.id'))
    version = Column(Integer, default=1)
    total_duration_sec = Column(Float, default=0.0)
    timeline_json = Column(JSON, nullable=True) # Full structured representation for exporter
    
    project = relationship("VideoProject", back_populates="timelines")
    clips = relationship("TimelineClip", back_populates="timeline", cascade="all, delete-orphan")

class TimelineClip(Base):
    __tablename__ = 'timeline_clips'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    timeline_id = Column(String(36), ForeignKey('timelines.id'))
    scene_id = Column(String(36), ForeignKey('scenes.id'), nullable=True)
    asset_id = Column(String(36), ForeignKey('assets.id'), nullable=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    layer = Column(Integer, default=0) # Z-index layer
    clip_type = Column(String(50), nullable=False) # VISUAL, AUDIO, SUBTITLE, EFFECT
    properties_json = Column(JSON, nullable=True) # Motion, transitions, styling attached to clip
    
    timeline = relationship("Timeline", back_populates="clips")

class RenderJob(Base):
    __tablename__ = 'render_jobs'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey('video_projects.id'))
    timeline_id = Column(String(36), ForeignKey('timelines.id'))
    status = Column(String(50), default="QUEUED") # QUEUED, PROCESSING, SUCCESS, FAILED
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    project = relationship("VideoProject", back_populates="render_jobs")
    result = relationship("RenderResult", back_populates="job", uselist=False, cascade="all, delete-orphan")

class RenderResult(Base):
    __tablename__ = 'render_results'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey('render_jobs.id'))
    output_path = Column(String(1000), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    
    job = relationship("RenderJob", back_populates="result")
    metadata_info = relationship("VideoMetadata", back_populates="result", uselist=False, cascade="all, delete-orphan")
    statistics = relationship("RenderStatistics", back_populates="result", uselist=False, cascade="all, delete-orphan")

class VideoMetadata(Base):
    __tablename__ = 'video_metadata'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    result_id = Column(String(36), ForeignKey('render_results.id'))
    resolution = Column(String(20), nullable=False)
    fps = Column(Integer, nullable=False)
    codec = Column(String(50), nullable=False)
    bitrate = Column(String(50), nullable=False)
    
    result = relationship("RenderResult", back_populates="metadata_info")

class RenderStatistics(Base):
    __tablename__ = 'render_statistics'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    result_id = Column(String(36), ForeignKey('render_results.id'))
    render_time_sec = Column(Float, nullable=False)
    frames_rendered = Column(Integer, nullable=True)
    hardware_accelerated = Column(Boolean, default=False)
    
    result = relationship("RenderResult", back_populates="statistics")

# --- Publishing Engine Models ---

class PublishedVideo(Base):
    __tablename__ = 'published_videos'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey('video_projects.id'))
    platform = Column(String(50), default="YOUTUBE")
    status = Column(String(50), default="PREPARING") # PREPARING, UPLOADING, PUBLISHED, FAILED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    project = relationship("VideoProject")
    attempts = relationship("UploadAttempt", back_populates="published_video", cascade="all, delete-orphan")
    metadata_info = relationship("PlatformMetadata", back_populates="published_video", uselist=False, cascade="all, delete-orphan")
    schedule = relationship("PublishingSchedule", back_populates="published_video", uselist=False, cascade="all, delete-orphan")
    result = relationship("PublishingResult", back_populates="published_video", uselist=False, cascade="all, delete-orphan")

class UploadAttempt(Base):
    __tablename__ = 'upload_attempts'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    published_video_id = Column(String(36), ForeignKey('published_videos.id'))
    attempt_number = Column(Integer, default=1)
    status = Column(String(50), default="IN_PROGRESS") # IN_PROGRESS, SUCCESS, FAILED
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    published_video = relationship("PublishedVideo", back_populates="attempts")

class PlatformMetadata(Base):
    __tablename__ = 'platform_metadata'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    published_video_id = Column(String(36), ForeignKey('published_videos.id'))
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    tags_json = Column(JSON, nullable=True)
    category_id = Column(String(20), nullable=True)
    visibility = Column(String(20), default="private")
    
    published_video = relationship("PublishedVideo", back_populates="metadata_info")

class PublishingSchedule(Base):
    __tablename__ = 'publishing_schedules'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    published_video_id = Column(String(36), ForeignKey('published_videos.id'))
    scheduled_for = Column(DateTime, nullable=False)
    is_published = Column(Boolean, default=False)
    
    published_video = relationship("PublishedVideo", back_populates="schedule")

class PublishingResult(Base):
    __tablename__ = 'publishing_results'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    published_video_id = Column(String(36), ForeignKey('published_videos.id'))
    platform_video_id = Column(String(100), nullable=False) # e.g. YouTube Video ID
    platform_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    
    published_video = relationship("PublishedVideo", back_populates="result")

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(50), nullable=False) # UPLOAD_SUCCESS, UPLOAD_FAILED
    message = Column(Text, nullable=False)
    level = Column(String(20), default="INFO")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_delivered = Column(Boolean, default=False)

# --- Learning Intelligence Engine Models ---

class AnalyticsSnapshot(Base):
    __tablename__ = 'analytics_snapshots'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    published_video_id = Column(String(36), ForeignKey('published_videos.id'))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    views = Column(Integer, default=0)
    ctr_percent = Column(Float, default=0.0)
    avg_view_duration_sec = Column(Float, default=0.0)
    retention_graph_json = Column(JSON, nullable=True)
    
    published_video = relationship("PublishedVideo")

class PerformanceReport(Base):
    __tablename__ = 'performance_reports'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    published_video_id = Column(String(36), ForeignKey('published_videos.id'))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    overall_score = Column(Float, nullable=True) # 0-100
    findings_json = Column(JSON, nullable=True)
    
    published_video = relationship("PublishedVideo")

class StrategyRecommendation(Base):
    __tablename__ = 'strategy_recommendations'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey('performance_reports.id'))
    target_engine = Column(String(50)) # e.g. 'RESEARCH', 'CONTENT', 'ASSET'
    recommendation_text = Column(Text, nullable=False)
    is_applied = Column(Boolean, default=False)
    
    report = relationship("PerformanceReport")

class KnowledgeEntry(Base):
    __tablename__ = 'knowledge_entries'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    category = Column(String(50), nullable=False) # HOOK_STYLE, THUMBNAIL_COLOR
    insight = Column(Text, nullable=False)
    confidence = Column(Float, default=0.5)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# --- Operations Platform Models ---

class QueueItem(Base):
    __tablename__ = 'queue_items'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), nullable=False)
    task_type = Column(String(50), nullable=False) # RESEARCH, CONTENT, ASSET, VIDEO, PUBLISH, LEARN
    payload_json = Column(JSON, nullable=True)
    status = Column(String(20), default="PENDING") # PENDING, IN_PROGRESS, COMPLETED, FAILED
    priority = Column(Integer, default=50) # Higher is more important
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    retries = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(50), nullable=False) # TASK_COMPLETED, TASK_FAILED, CEO_DECISION
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
class OperationDecision(Base):
    __tablename__ = 'operation_decisions'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    decision_type = Column(String(50), nullable=False) # GENERATE_VIDEO, PAUSE, REGENERATE
    justification = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class RecoveryCheckpoint(Base):
    __tablename__ = 'recovery_checkpoints'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), nullable=False)
    last_successful_task = Column(String(50), nullable=False)
    state_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Asset(Base):
    __tablename__ = 'assets'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    package_id = Column(String(36), ForeignKey('asset_packages.id'))
    scene_id = Column(String(36), ForeignKey('scenes.id'), nullable=True) # Global assets (e.g. voice) might not map to a single visual scene
    asset_type = Column(String(50), nullable=False) # IMAGE, VOICE, SUBTITLE, etc.
    provider = Column(String(100), nullable=False)
    file_path = Column(String(1000), nullable=True)
    creation_time = Column(DateTime, default=datetime.utcnow)
    checksum = Column(String(200), nullable=True)
    reuse_status = Column(Boolean, default=False)
    
    package = relationship("AssetPackage", back_populates="assets")
    # Using polymorphic identity for specific asset types if needed, or simple relationships
    validation = relationship("AssetValidation", back_populates="asset", uselist=False, cascade="all, delete-orphan")

class GeneratedImage(Base):
    __tablename__ = 'generated_images'
    id = Column(String(36), ForeignKey('assets.id'), primary_key=True)
    prompt = Column(Text, nullable=False)
    style = Column(String(100), nullable=True)

class FetchedAsset(Base):
    __tablename__ = 'fetched_assets'
    id = Column(String(36), ForeignKey('assets.id'), primary_key=True)
    source_url = Column(String(1000), nullable=False)

class VoiceTrack(Base):
    __tablename__ = 'voice_tracks'
    id = Column(String(36), ForeignKey('assets.id'), primary_key=True)
    text = Column(Text, nullable=False)
    duration_seconds = Column(Float, nullable=True)

class SubtitleTrack(Base):
    __tablename__ = 'subtitle_tracks'
    id = Column(String(36), ForeignKey('assets.id'), primary_key=True)
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    speaker = Column(String(100), nullable=True)

class AssetValidation(Base):
    __tablename__ = 'asset_validations'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    asset_id = Column(String(36), ForeignKey('assets.id'))
    status = Column(String(50), default="PENDING") # PENDING, PASSED, FAILED
    report_json = Column(JSON, nullable=True)
    
    asset = relationship("Asset", back_populates="validation")

# --- Infrastructure Models ---

class BackupRecord(Base):
    __tablename__ = 'backup_records'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    backup_type = Column(String(50), nullable=False) # FULL, DATABASE, CONFIG, KNOWLEDGE
    file_path = Column(String(1000), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    status = Column(String(20), default="COMPLETED") # COMPLETED, FAILED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class RestoreRecord(Base):
    __tablename__ = 'restore_records'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    backup_id = Column(String(36), ForeignKey('backup_records.id'))
    status = Column(String(20), default="COMPLETED")
    restored_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    backup = relationship("BackupRecord")

class CredentialStatus(Base):
    __tablename__ = 'credential_statuses'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    provider_name = Column(String(100), nullable=False)
    is_valid = Column(Boolean, default=True)
    last_checked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    error_message = Column(Text, nullable=True)

class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    alert_type = Column(String(50), nullable=False) # DISK_FULL, PROVIDER_DOWN, QUEUE_GROWTH
    severity = Column(String(20), default="WARNING") # INFO, WARNING, CRITICAL
    message = Column(Text, nullable=False)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class MaintenanceTask(Base):
    __tablename__ = 'maintenance_tasks'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_type = Column(String(50), nullable=False) # LOG_CLEANUP, ASSET_CLEANUP, DB_OPTIMIZE
    status = Column(String(20), default="COMPLETED")
    items_processed = Column(Integer, default=0)
    executed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class DiagnosticReport(Base):
    __tablename__ = 'diagnostic_reports'
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_type = Column(String(50), nullable=False) # SYSTEM, PROVIDER, DATABASE, PERFORMANCE
    findings_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

