import os
import sys
import time
import threading

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import init_db
from database.session import get_db_session

from operations.event_bus.bus import EventBus
from operations.task_queue.queue import TaskQueue
from operations.resource_manager.manager import ResourceManager
from operations.health_monitor.monitor import HealthMonitor
from operations.recovery_manager.manager import RecoveryManager
from operations.scheduler.scheduler import Scheduler
from operations.dispatcher.dispatcher import Dispatcher

from operations.decision_engine.engine import DecisionEngine
from operations.workflow_planner.planner import WorkflowPlanner
from operations.ceo_agent.agent import CEOAgent

from operations.dashboard.terminal import TerminalDashboard

# Infrastructure services
from infrastructure.credential_manager.manager import CredentialManager
from infrastructure.alerting.notifier import AlertEngine
from infrastructure.backup.manager import BackupManager
from infrastructure.maintenance.janitor import Janitor
from infrastructure.audit.logger import AuditLogger

def start_dispatcher(dispatcher: Dispatcher):
    while True:
        dispatcher.tick()
        time.sleep(2) # Polling interval

def run_operations():
    init_db()
    
    # --- 1. Core Services ---
    db = get_db_session().__enter__() # Keep session alive for the daemon thread
    
    AuditLogger.log("SYSTEM_STARTUP", "Operations", {"phase": "initialization"})
    
    bus = EventBus()
    queue = TaskQueue(db)
    resource_mgr = ResourceManager()
    health_mon = HealthMonitor(db, resource_mgr)
    
    # --- 2. Infrastructure Pre-flight ---
    cred_mgr = CredentialManager(db)
    cred_mgr.check_all()
    
    alert_engine = AlertEngine(db)
    alert_engine.check_all()
    
    # --- 3. Recovery ---
    recovery_mgr = RecoveryManager(db)
    recovery_mgr.recover()
    
    # --- 4. Intelligence ---
    decision_engine = DecisionEngine()
    workflow_planner = WorkflowPlanner(queue, bus)
    ceo_agent = CEOAgent(db, decision_engine, workflow_planner)
    
    # --- 5. Dispatcher ---
    dispatcher = Dispatcher(db, queue, bus, resource_mgr)
    
    # --- 6. Scheduler ---
    scheduler = Scheduler()
    scheduler.start()
    
    # CEO strategic cycle every 1 minute (testing), alerts every 5 minutes, backup daily (1440 min)
    scheduler.add_job(1, ceo_agent.execute_strategic_cycle)
    scheduler.add_job(5, alert_engine.check_all)
    
    backup_mgr = BackupManager(db)
    janitor = Janitor(db)
    scheduler.add_job(1440, backup_mgr.backup_full)
    scheduler.add_job(720, janitor.run_all)
    
    # --- 7. Threads ---
    dispatch_thread = threading.Thread(target=start_dispatcher, args=(dispatcher,), daemon=True)
    dispatch_thread.start()
    
    # Kick off an initial CEO cycle right away
    ceo_agent.execute_strategic_cycle()
    
    AuditLogger.log("SYSTEM_READY", "Operations", {"status": "all_systems_nominal"})
    
    # --- 8. Dashboard (Blocks main thread) ---
    dashboard = TerminalDashboard(db)
    try:
        dashboard.start()
    except KeyboardInterrupt:
        print("\nShutting down AI Operations...")
        AuditLogger.log("SYSTEM_SHUTDOWN", "Operations", {"reason": "user_interrupt"})
    finally:
        scheduler.stop()
        db.close()

if __name__ == "__main__":
    run_operations()
