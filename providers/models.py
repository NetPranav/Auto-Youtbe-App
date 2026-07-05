from enum import Enum

class TaskCategory(str, Enum):
    # Research Engine
    RESEARCH_TOPIC_EXTRACTION = "research_topic_extraction"
    RESEARCH_TOPIC_RANKING = "research_topic_ranking"
    RESEARCH_NOVELTY_ANALYSIS = "research_novelty_analysis"
    
    # Content Engine
    CONTENT_STRATEGY = "content_strategy"
    CONTENT_HOOK_GENERATION = "content_hook_generation"
    CONTENT_OUTLINE_GENERATION = "content_outline_generation"
    CONTENT_SCRIPT_WRITING = "content_script_writing"
    CONTENT_FACT_CHECKING = "content_fact_checking"
    CONTENT_SCRIPT_REVIEW = "content_script_review"
    CONTENT_RETENTION_ANALYSIS = "content_retention_analysis"
    CONTENT_SCENE_PLANNING = "content_scene_planning"
    CONTENT_SEO_GENERATION = "content_seo_generation"
    
    # Defaults
    DEFAULT_REASONING = "default_reasoning"
    DEFAULT_CREATIVE = "default_creative"
    DEFAULT_FAST = "default_fast"
    DEFAULT_IMAGE = "default_image"
