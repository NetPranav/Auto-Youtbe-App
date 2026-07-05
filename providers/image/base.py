from typing import Optional
from providers.models import TaskCategory

class BaseImageProvider:
    def generate_image(self, prompt: str, output_dir: str, task_category: TaskCategory = TaskCategory.DEFAULT_IMAGE) -> Optional[str]:
        raise NotImplementedError
