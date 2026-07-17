import uuid
from typing import Dict, Any
from common import logger
from operations.task_queue.queue import TaskQueue
from operations.event_bus.bus import EventBus



class WorkflowPlanner:
    def __init__(self, queue: TaskQueue, bus: EventBus):
        self.queue = queue
        self.bus = bus
        
        # Subscribe to completion events to trigger the next step
        self.bus.subscribe("TASK_COMPLETED", self._on_task_completed)
        self.bus.subscribe("TASK_FAILED", self._on_task_failed)
        
    def start_new_workflow(self, topic: str):
        workflow_id = str(uuid.uuid4())
        logger.info(f"[WorkflowPlanner] Planning new workflow {workflow_id} for topic: {topic}")
        
        # 1. Research
        self.queue.enqueue(
            workflow_id=workflow_id,
            task_type="RESEARCH",
            payload={"topic": topic},
            priority=50
        )
        
    def _on_task_completed(self, payload: Dict[str, Any]):
        task_type = payload.get("task_type")
        workflow_id = payload.get("workflow_id")
        task_payload = payload.get("payload", {})
        
        logger.info(f"[WorkflowPlanner] Task {task_type} completed for {workflow_id}. Planning next step...")
        
        # Standard Linear Pipeline defined implicitly here via Event Chaining
        if task_type == "RESEARCH":
            self.queue.enqueue(workflow_id, "CONTENT", task_payload)
        elif task_type == "CONTENT":
            self.queue.enqueue(workflow_id, "ASSET", task_payload)
        elif task_type == "ASSET":
            self.queue.enqueue(workflow_id, "VIDEO", task_payload)
        elif task_type == "VIDEO":
            self.queue.enqueue(workflow_id, "PUBLISH", task_payload)
        elif task_type == "PUBLISH":
            self.queue.enqueue(workflow_id, "LEARN", task_payload)
        elif task_type == "LEARN":
            logger.info(f"[WorkflowPlanner] === Workflow {workflow_id} fully complete! ===")
            
    def _on_task_failed(self, payload: Dict[str, Any]):
        task_type = payload.get("task_type")
        workflow_id = payload.get("workflow_id")
        logger.error(f"[WorkflowPlanner] Workflow {workflow_id} halted due to failure in {task_type}.")
