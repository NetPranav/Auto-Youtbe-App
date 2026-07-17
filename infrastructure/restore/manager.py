import os
import shutil
import zipfile
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from common import logger
from database.models import BackupRecord, RestoreRecord



class RestoreManager:
    """
    Restores data from a previously created backup archive.
    """
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def restore_from_backup(self, backup_id: str) -> bool:
        logger.info(f"[RestoreManager] Initiating restore from backup {backup_id}...")
        
        record = self.db.query(BackupRecord).filter(BackupRecord.id == backup_id).first()
        if not record:
            logger.error(f"[RestoreManager] Backup record {backup_id} not found.")
            return False
            
        if not os.path.exists(record.file_path):
            logger.error(f"[RestoreManager] Backup file missing: {record.file_path}")
            return False
            
        # Extract to a temp location
        extract_dir = "backups/_restore_staging"
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(record.file_path, 'r') as zf:
                zf.extractall(extract_dir)
                
            # Copy extracted files back to project root
            for item in os.listdir(extract_dir):
                src = os.path.join(extract_dir, item)
                dst = item  # Relative to project root
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
                    
            restore = RestoreRecord(
                backup_id=backup_id,
                status="COMPLETED"
            )
            self.db.add(restore)
            self.db.commit()
            
            logger.info(f"[RestoreManager] Restore from {record.file_path} completed successfully.")
            return True
            
        except Exception as e:
            logger.error(f"[RestoreManager] Restore failed: {e}")
            return False
        finally:
            shutil.rmtree(extract_dir, ignore_errors=True)
