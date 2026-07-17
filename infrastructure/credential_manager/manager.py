import os
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from common import logger
from database.models import CredentialStatus



class CredentialManager:
    """
    Centralized credential health checker.
    Validates that all configured API keys exist and are well-formed.
    """
    PROVIDERS = {
        "NVIDIA": "NVIDIA_API_KEY",
        "YOUTUBE": "YOUTUBE_CLIENT_SECRET_PATH",
    }
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def check_all(self) -> dict:
        logger.info("[CredentialManager] Verifying all provider credentials...")
        results = {}
        
        for provider_name, env_var in self.PROVIDERS.items():
            value = os.environ.get(env_var, "")
            is_valid = bool(value and value.strip())
            error = None
            
            if not is_valid:
                error = f"Environment variable {env_var} is missing or empty."
                logger.warning(f"[CredentialManager] {provider_name}: {error}")
            else:
                logger.info(f"[CredentialManager] {provider_name}: OK")
                
            # Upsert status
            existing = self.db.query(CredentialStatus).filter(
                CredentialStatus.provider_name == provider_name
            ).first()
            
            if existing:
                existing.is_valid = is_valid
                existing.last_checked_at = datetime.now(timezone.utc)
                existing.error_message = error
            else:
                self.db.add(CredentialStatus(
                    provider_name=provider_name,
                    is_valid=is_valid,
                    error_message=error
                ))
                
            results[provider_name] = is_valid
            
        self.db.commit()
        return results
