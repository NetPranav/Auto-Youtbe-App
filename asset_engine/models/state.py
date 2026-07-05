from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AssetRequest(BaseModel):
    scene_id: str
    asset_type: str  # IMAGE, FETCHED_LOGO, FETCHED_SCREENSHOT, VOICE, SUBTITLE
    provider_type: str # DALL-E, PEXELS, MOCK, etc.
    parameters: Dict[str, Any] # Prompts, URLs, text for voice
    priority: int = 1
    fallback_provider: Optional[str] = None
    expected_dimensions: Optional[str] = None

class AssetResult(BaseModel):
    request: AssetRequest
    file_path: Optional[str] = None
    status: str # SUCCESS, FAILED
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
class AssetPackageData(BaseModel):
    content_package_id: str
    assets: List[AssetResult] = []
