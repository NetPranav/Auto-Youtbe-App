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

def start_dispatcher(dispatcher: Dispatcher):
    while True:
        dispatcher.tick()
        time.sleep(2) # Polling interval

def run_operations():
    init_db()
    
    # --- 1. Core Services ---
    db = get_db_session().__enter__() # Keep session alive for the daemon thread
    
    bus = EventBus()
    queue = TaskQueue(db)
    resource_mgr = ResourceManager()
    health_mon = HealthMonitor(db, resource_mgr)
    
    # --- 2. Recovery ---
    recovery_mgr = RecoveryManager(db)
    recovery_mgr.recover()
    
    # --- 3. Intelligence ---
    decision_engine = DecisionEngine()
    workflow_planner = WorkflowPlanner(queue, bus)
    ceo_agent = CEOAgent(db, decision_engine, workflow_planner)
    
    # --- 4. Dispatcher ---
    dispatcher = Dispatcher(db, queue, bus, resource_mgr)
    
    # --- 5. Scheduler ---
    scheduler = Scheduler()
    scheduler.start()
    
    # Schedule CEO check every 1 minute for testing (Normally hourly/daily)
    scheduler.add_job(1, ceo_agent.execute_strategic_cycle)
    
    # --- 6. Threads ---
    # Start dispatcher loop in background
    dispatch_thread = threading.Thread(target=start_dispatcher, args=(dispatcher,), daemon=True)
    dispatch_thread.start()
    
    # Kick off an initial CEO cycle right away
    ceo_agent.execute_strategic_cycle()
    
    # --- 7. Dashboard (Blocks main thread) ---
    dashboard = TerminalDashboard(db)
    try:
        dashboard.start()
    except KeyboardInterrupt:
        print("\nShutting down AI Operations...")
    finally:
        scheduler.stop()
        db.close()

if __name__ == "__main__":
    run_operations()
