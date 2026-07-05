import os
import uuid
import time
from typing import Optional
from common import logger
from .base import BaseImageProvider
from providers.models import TaskCategory
from providers.statistics import ProviderStatistics

class MockImageProvider(BaseImageProvider):
    def generate_image(self, prompt: str, output_dir: str, task_category: TaskCategory = TaskCategory.DEFAULT_IMAGE) -> Optional[str]:
        start_time = time.time()
        time.sleep(0.01)
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            file_name = f"img_{uuid.uuid4().hex[:8]}.png"
            file_path = os.path.join(output_dir, file_name)
            
            with open(file_path, "wb") as f:
                f.write(b"mock_image_data")
                
            execution_time = (time.time() - start_time) * 1000
            ProviderStatistics.log_request(
                provider_name="MockImage",
                model_used="mock-image-model",
                request_type="generate_image",
                task_category=task_category,
                execution_time_ms=execution_time,
                success=True
            )
            return file_path
        except Exception as e:
            logger.error(f"[MockImage] Failed to generate mock image: {e}")
            return None
