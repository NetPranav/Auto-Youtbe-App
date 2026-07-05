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


