import os
import requests
import base64
import uuid
from typing import Optional
from common import logger
from config import config
from .base import BaseImageProvider

class NimImageProvider(BaseImageProvider):
    def generate_image(self, prompt: str, output_dir: str) -> Optional[str]:
        api_key = config.nvidia_nim_api_key
        if not api_key:
            logger.error("NVIDIA_NIM_API_KEY is not set. Cannot generate image.")
            return None
            
        url = "https://integrate.api.nvidia.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "prompt": prompt,
            "model": "stabilityai/stable-diffusion-xl",
            "n": 1,
            "size": "1024x1024",
            "response_format": "b64_json"
        }
        
        try:
            logger.info(f"[NIM Image] Requesting image for prompt: {prompt[:30]}...")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                b64_data = data["data"][0]["b64_json"]
                image_bytes = base64.b64decode(b64_data)
                
                os.makedirs(output_dir, exist_ok=True)
                file_path = os.path.join(output_dir, f"nim_image_{uuid.uuid4().hex[:8]}.png")
                
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                
                logger.info(f"[NIM Image] Successfully saved image to {file_path}")
                return file_path
            else:
                logger.error("[NIM Image] API returned no image data.")
                return None
        except Exception as e:
            logger.error(f"[NIM Image] API request failed: {e}", exc_info=True)
            return None
