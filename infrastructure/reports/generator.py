import json
import os
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from common.logger import get_logger
from infrastructure.diagnostics.engine import DiagnosticsEngine

logger = get_logger(__name__)

REPORTS_DIR = os.path.join("logs", "reports")

class ReportGenerator:
    """
    Generates and archives daily/weekly/monthly infrastructure reports.
    """
    def __init__(self, db_session: Session):
        self.db = db_session
        os.makedirs(REPORTS_DIR, exist_ok=True)
        
    def generate_daily(self) -> str:
        logger.info("[ReportGenerator] Generating daily infrastructure report...")
        
        diag = DiagnosticsEngine(self.db)
        findings = diag.run_full_diagnostic()
        
        report = {
            "report_type": "DAILY",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "diagnostics": findings
        }
        
        filename = f"daily_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=4)
            
        logger.info(f"[ReportGenerator] Daily report saved: {filepath}")
        return filepath
