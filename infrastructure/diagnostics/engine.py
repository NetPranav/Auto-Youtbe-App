from sqlalchemy.orm import Session
from common import logger
from database.models import DiagnosticReport, QueueItem, Alert
from infrastructure.profiling.profiler import Profiler
from infrastructure.credential_manager.manager import CredentialManager



class DiagnosticsEngine:
    """
    Generates comprehensive system diagnostic reports.
    """
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def run_full_diagnostic(self) -> dict:
        logger.info("[Diagnostics] Running full system diagnostic...")
        
        # 1. System Performance
        perf = Profiler.snapshot()
        
        # 2. Credential Health
        cred_mgr = CredentialManager(self.db)
        cred_status = cred_mgr.check_all()
        
        # 3. Queue Health
        pending = self.db.query(QueueItem).filter(QueueItem.status == "PENDING").count()
        failed = self.db.query(QueueItem).filter(QueueItem.status == "FAILED").count()
        completed = self.db.query(QueueItem).filter(QueueItem.status == "COMPLETED").count()
        
        # 4. Active Alerts
        active_alerts = self.db.query(Alert).filter(Alert.is_acknowledged == False).count()
        
        findings = {
            "system_performance": perf,
            "credentials": cred_status,
            "queue": {
                "pending": pending,
                "failed": failed,
                "completed": completed
            },
            "active_alerts": active_alerts
        }
        
        report = DiagnosticReport(
            report_type="SYSTEM",
            findings_json=findings
        )
        self.db.add(report)
        self.db.commit()
        
        logger.info(f"[Diagnostics] Report saved. CPU: {perf['cpu_percent']}%, RAM: {perf['ram_used_percent']}%, Alerts: {active_alerts}")
        return findings
