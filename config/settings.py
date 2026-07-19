"""
Centralized Configuration Module.
Loads environment variables and validates them using Pydantic.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Application Settings.
    All variables here should match the variables in the .env file.
    """
    
    environment: str = Field(default="development", description="Running environment (development/production)")
    database_url: str = Field(..., description="SQLAlchemy compatible database connection string")
    
    log_level: str = Field(default="INFO", description="Minimum log level to output")
    log_file_path: str = Field(default="logs/app.log", description="Path to the log file")
    
    # Debug & Diagnostics
    debug_mode: bool = Field(default=False, description="Enable saving of intermediate outputs and prompts")
    debug_output_dir: str = Field(default="debug_outputs", description="Directory to save debug logs and state dumps")
    
    # Research Engine Settings
    research_enabled_sources: str = Field(default="rss,hackernews", description="Comma separated list of active sources")
    research_max_articles_per_source: int = Field(default=20, description="Max articles to scrape per source")
    
    # Topic Ranker Weights
    weight_novelty: float = Field(default=1.5)
    weight_audience: float = Field(default=1.2)
    weight_educational: float = Field(default=1.0)
    weight_recency: float = Field(default=1.5)
    weight_competition: float = Field(default=0.8) # Lower score = higher competition (invert later)
    weight_search_interest: float = Field(default=1.0)

    # Content Engine Settings
    content_max_optimization_loops: int = Field(default=3, description="Maximum number of script revisions")
    content_min_fact_score: float = Field(default=0.9, description="Minimum score to pass fact checking")
    content_min_retention_score: float = Field(default=0.8, description="Minimum score to pass retention analyzer")
    
    # Asset Engine Settings
    asset_storage_dir: str = Field(default="assets", description="Directory to store generated assets")
    # Video Generation Defaults
    asset_video_resolution: str = Field(default="1080x1920", description="Target resolution for generated video")
    video_fps: int = Field(default=30, env="VIDEO_FPS")
    video_bitrate: str = Field(default="5M", env="VIDEO_BITRATE")
    video_codec: str = Field(default="libx264", env="VIDEO_CODEC")
    video_hardware_encoding: str = Field(default="none", env="VIDEO_HARDWARE_ENCODING") # none, nvenc, qsv, videotoolbox
    video_motion_intensity: float = Field(default=1.0, env="VIDEO_MOTION_INTENSITY")
    
    # Publishing Engine Defaults
    youtube_client_secret_path: str = Field(default="client_secret.json", env="YOUTUBE_CLIENT_SECRET_PATH")
    youtube_default_visibility: str = Field(default="private", env="YOUTUBE_DEFAULT_VISIBILITY")
    youtube_default_category_id: str = Field(default="28", description="Science & Technology", env="YOUTUBE_DEFAULT_CATEGORY_ID")
    publishing_max_retries: int = Field(default=3, env="PUBLISHING_MAX_RETRIES")
    publishing_chunk_size_mb: int = Field(default=5, env="PUBLISHING_CHUNK_SIZE_MB")
    
    # Providers Default Settings
    image_provider: str = Field(default="nim", description="Provider for image generation (e.g. nim, dall-e)")
    voice_provider: str = Field(default="edge_tts", description="Provider for voice generation (e.g. edge_tts, elevenlabs)")
    stock_provider: str = Field(default="pexels", description="Provider for stock video/images")
    ai_text_provider: str = Field(default="nim", description="Provider for text LLM generation")
    
    # NVIDIA NIM Configurations
    nvidia_nim_api_key: str = Field(default="", env="NVIDIA_NIM_API_KEY")
    nvidia_base_url: str = Field(default="https://integrate.api.nvidia.com/v1", env="NVIDIA_BASE_URL")
    
    # New Providers (Gemini / ElevenLabs)
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    elevenlabs_api_key: str = Field(default="", env="ELEVENLABS_API_KEY")
    
    # Fine-Grained Model Routing (Preferred Models)
    research_model: str = Field(default="meta/llama-3.1-70b-instruct", env="RESEARCH_MODEL")
    topic_extraction_model: str = Field(default="meta/llama-3.1-70b-instruct", env="TOPIC_EXTRACTION_MODEL")
    topic_ranking_model: str = Field(default="meta/llama-3.1-70b-instruct", env="TOPIC_RANKING_MODEL")
    script_strategy_model: str = Field(default="meta/llama-3.1-70b-instruct", env="SCRIPT_STRATEGY_MODEL")
    hook_generation_model: str = Field(default="meta/llama-3.1-70b-instruct", env="HOOK_GENERATION_MODEL")
    outline_model: str = Field(default="meta/llama-3.1-70b-instruct", env="OUTLINE_MODEL")
    script_model: str = Field(default="meta/llama-3.1-70b-instruct", env="SCRIPT_MODEL")
    fact_check_model: str = Field(default="meta/llama-3.1-70b-instruct", env="FACT_CHECK_MODEL")
    script_review_model: str = Field(default="meta/llama-3.1-70b-instruct", env="SCRIPT_REVIEW_MODEL")
    retention_model: str = Field(default="meta/llama-3.1-70b-instruct", env="RETENTION_MODEL")
    scene_planner_model: str = Field(default="meta/llama-3.1-70b-instruct", env="SCENE_PLANNER_MODEL")
    seo_model: str = Field(default="meta/llama-3.1-70b-instruct", env="SEO_MODEL")
    image_prompt_model: str = Field(default="meta/llama-3.1-70b-instruct", env="IMAGE_PROMPT_MODEL")

    
    default_image_model: str = Field(default="stabilityai/stable-diffusion-xl", env="DEFAULT_IMAGE_MODEL")
    request_timeout: int = Field(default=60, env="REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    
    # API Keys (Other)
    pexels_api_key: str = Field(default="", env="PEXELS_API_KEY")
    asset_output_resolution: str = Field(default="1920x1080")
    asset_voice_style: str = Field(default="energetic")
    
    # The config dict specifies where to look for the environment variables
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Instantiate the global configuration object to be imported by engines.
# It will automatically parse the .env file upon startup.
config = Settings()
