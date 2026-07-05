import os
import shutil
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from common.logger import get_logger
from database.models import BackupRecord

logger = get_logger(__name__)

class BackupManager:
    """
    Creates timestamped ZIP archives of critical data.
    Supports FULL, DATABASE, CONFIG, and KNOWLEDGE backup types.
    """
    BACKUP_DIR = "backups"
    
    TARGETS = {
        "DATABASE": ["youtube_automation.db"],
        "CONFIG": [".env", "config"],
        "KNOWLEDGE": ["data"],
        "PROMPTS": [
            "research_engine/prompts",
            "content_engine/prompts",
            "publisher/prompts",
            "learning_engine/prompts"
        ]
    }
    
    def __init__(self, db_session: Session):
        self.db = db_session
        os.makedirs(self.BACKUP_DIR, exist_ok=True)
        
    def backup_full(self) -> str:
        logger.info("[BackupManager] Starting FULL backup...")
        all_paths = []
        for paths in self.TARGETS.values():
            all_paths.extend(paths)
        return self._create_archive("FULL", all_paths)
        
    def backup_database(self) -> str:
        return self._create_archive("DATABASE", self.TARGETS["DATABASE"])
        
    def backup_config(self) -> str:
        return self._create_archive("CONFIG", self.TARGETS["CONFIG"])
        
    def _create_archive(self, backup_type: str, paths: list) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_name = f"{backup_type.lower()}_{timestamp}"
        archive_path = os.path.join(self.BACKUP_DIR, archive_name)
        
        # Create a temp directory with the files to backup
        staging = os.path.join(self.BACKUP_DIR, f"_staging_{timestamp}")
        os.makedirs(staging, exist_ok=True)
        
        for path in paths:
            if os.path.exists(path):
                dest = os.path.join(staging, os.path.basename(path))
                if os.path.isdir(path):
                    shutil.copytree(path, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(path, dest)
                    
        # Create ZIP
        final_path = shutil.make_archive(archive_path, 'zip', staging)
        shutil.rmtree(staging, ignore_errors=True)
        
        file_size = os.path.getsize(final_path)
        
        record = BackupRecord(
            backup_type=backup_type,
            file_path=final_path,
            file_size_bytes=file_size,
            status="COMPLETED"
        )
        self.db.add(record)
        self.db.commit()
        
        logger.info(f"[BackupManager] {backup_type} backup created: {final_path} ({file_size} bytes)")
        return final_path
