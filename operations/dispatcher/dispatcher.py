from sqlalchemy.orm import Session
from common import logger
from operations.task_queue.queue import TaskQueue
from operations.event_bus.bus import EventBus
from operations.resource_manager.manager import ResourceManager
from providers.manager import ProviderManager

from infrastructure.tracing.tracer import new_trace
from infrastructure.metrics.collector import track_metric
from infrastructure.audit.logger import AuditLogger

# Import engines
from research_engine.engine import ResearchEngine
from content_engine.engine import ContentEngine
from asset_engine.engine import AssetEngine
from video_engine.engine import VideoEngine
from publisher.engine import PublishingEngine
from learning_engine.engine import LearningEngine



class Dispatcher:
    """
    Safely executes tasks from the queue and maps them to engine invocations.
    All tracing, metrics, and audit logging hooks are applied here so engines remain untouched.
    """
    def __init__(self, db_session: Session, queue: TaskQueue, bus: EventBus, resource_manager: ResourceManager):
        self.db = db_session
        self.queue = queue
        self.bus = bus
        self.resource_manager = resource_manager
        self.provider_manager = ProviderManager()
        
    def tick(self):
        """Called periodically by the main operations loop to dispatch tasks."""
        if not self.resource_manager.can_accept_task():
            return
            
        item = self.queue.dequeue()
        if not item:
            return
            
        # Start a distributed trace for this task
        trace_id = new_trace(workflow_id=item.workflow_id)
        
        logger.info(f"[Dispatcher] Starting task {item.task_type} (ID: {item.id}, Trace: {trace_id})")
        AuditLogger.log("TASK_DISPATCHED", "Dispatcher", {"task_type": item.task_type, "workflow_id": item.workflow_id})
        
        success = False
        try:
            success = self._execute_task_tracked(item)
        except Exception as e:
            logger.error(f"[Dispatcher] Unhandled exception in task {item.task_type}: {e}")
            success = False
            
        if success:
            self.queue.complete(item.id)
            self.bus.publish("TASK_COMPLETED", {"task_type": item.task_type, "workflow_id": item.workflow_id, "payload": item.payload_json})
            AuditLogger.log("TASK_COMPLETED", "Dispatcher", {"task_type": item.task_type})
        else:
            self.queue.fail(item.id, "Task execution returned False or crashed.")
            self.bus.publish("TASK_FAILED", {"task_type": item.task_type, "workflow_id": item.workflow_id})
            AuditLogger.log("TASK_FAILED", "Dispatcher", {"task_type": item.task_type})

    @track_metric("engine_execution_time")
    def _execute_task_tracked(self, item) -> bool:
        return self._execute_task(item)

    def _execute_task(self, item) -> bool:
        if item.task_type == "RESEARCH":
            engine = ResearchEngine(self.db, self.provider_manager)
            topic = item.payload_json.get("topic", "Technology News")
            pkg_id = engine.run(topic)
            if pkg_id:
                # Store the result back in the payload for the next step
                item.payload_json["research_package_id"] = pkg_id
                self.db.commit()
                return True
            return False
            
        elif item.task_type == "CONTENT":
            engine = ContentEngine(self.db, self.provider_manager)
            pkg_id = item.payload_json.get("research_package_id")
            res_id = engine.run(pkg_id)
            if res_id:
                item.payload_json["content_package_id"] = res_id
                self.db.commit()
                return True
            return False
            
        elif item.task_type == "ASSET":
            engine = AssetEngine(self.db, self.provider_manager)
            pkg_id = item.payload_json.get("content_package_id")
            res_id = engine.run(pkg_id)
            if res_id:
                item.payload_json["asset_package_id"] = res_id
                self.db.commit()
                return True
            return False
            
        elif item.task_type == "VIDEO":
            engine = VideoEngine(self.db)
            pkg_id = item.payload_json.get("asset_package_id")
            res_id = engine.run(pkg_id)
            if res_id:
                # Video project id is derived in Publisher step normally, but we can pass it here.
                # Actually, video engine returns path. Let's just return true.
                return True
            return False
            
        elif item.task_type == "PUBLISH":
            engine = PublishingEngine(self.db, self.provider_manager)
            # Find the VideoProject for the asset package
            pkg_id = item.payload_json.get("asset_package_id")
            from database.models import VideoProject
            vp = self.db.query(VideoProject).filter(VideoProject.asset_package_id == pkg_id).order_by(VideoProject.created_at.desc()).first()
            if vp:
                url = engine.run(vp.id)
                return url is not None
            return False
            
        elif item.task_type == "LEARN":
            engine = LearningEngine(self.db, self.provider_manager)
            engine.run()
            return True
            
        return False
