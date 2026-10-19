import os
import uuid
from typing import Optional
from common import logger
from asset_engine.providers.base import BaseVoiceProvider
from common.retry_helpers import with_retry

class BarkProvider(BaseVoiceProvider):
    @property
    def provider_name(self) -> str:
        return "BarkTTS"

    def __init__(self):
        # Enforce CPU offloading for 8GB VRAM (RTX 4060)
        os.environ["SUNO_OFFLOAD_CPU"] = "True"
        
        # We only import bark locally to avoid slow startup if it's not being used
        try:
            from bark import SAMPLE_RATE, generate_audio, preload_models
            import torch
            import scipy.io.wavfile as wavfile
            self.SAMPLE_RATE = SAMPLE_RATE
            self.generate_audio = generate_audio
            self.wavfile = wavfile
            
            # PyTorch 2.6+ defaults weights_only=True which breaks older libraries like Bark.
            # We monkey-patch torch.load to bypass this for Bark's preload_models.
            original_load = torch.load
            def safe_load(*args, **kwargs):
                kwargs.setdefault('weights_only', False)
                return original_load(*args, **kwargs)
            torch.load = safe_load
            
            logger.info("[BarkTTS] Preloading Bark models (this may take a moment)...")
            # preload_models will automatically utilize CUDA if available
            preload_models()
            logger.info("[BarkTTS] Models loaded successfully.")
        except ImportError as e:
            logger.error(f"[BarkTTS] Failed to import Bark/PyTorch dependencies: {e}. Please ensure suno-bark is installed.")
            raise

    @with_retry(max_retries=2, delay=5, backoff=2)
    def generate_voice(self, text: str, output_dir: str, genre: str = "ROMANCE") -> Optional[str]:
        try:
            import re
            import numpy as np
            
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"voice_{uuid.uuid4().hex[:8]}.wav")
            
            logger.info(f"[BarkTTS] Generating voice for full script (Length: {len(text)} chars) with genre {genre}")
            
            # Map genres to specific Bark voice models
            genre = genre.upper()
            if genre == "HORROR":
                speaker = "v2/en_speaker_0" # Deep, serious male
            elif genre == "SPORTS":
                speaker = "v2/en_speaker_1" # Energetic male
            elif genre == "COMEDY":
                speaker = "v2/en_speaker_4" # Upbeat male
            else: # ROMANCE / DEFAULT
                speaker = "v2/en_speaker_9" # Warm storytelling voice
                
            # Bark has a strict ~14 second generation limit per call.
            # We must split the script into sentences and concatenate the audio arrays.
            # Split by punctuation followed by space or newline
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', text) if s.strip()]
            
            pieces = []
            for i, sentence in enumerate(sentences):
                logger.debug(f"[BarkTTS] Generating chunk {i+1}/{len(sentences)}: '{sentence[:30]}...'")
                audio_array = self.generate_audio(sentence, history_prompt=speaker)
                pieces.append(audio_array)
                # Add a tiny pause between sentences to sound natural
                silence = np.zeros(int(0.25 * self.SAMPLE_RATE), dtype=np.float32)
                pieces.append(silence)
                
            if not pieces:
                logger.error("[BarkTTS] No audio chunks generated.")
                return None
                
            final_audio = np.concatenate(pieces)
            
            # Save to disk as WAV (temporary)
            temp_path = file_path.replace(".wav", "_temp.wav")
            self.wavfile.write(temp_path, self.SAMPLE_RATE, final_audio)
            
            # Speed up by 1.25x using ffmpeg to fix the slow speaking pace for Shorts
            import subprocess
            logger.info("[BarkTTS] Applying 1.25x speedup via FFmpeg atempo filter...")
            subprocess.run([
                "ffmpeg", "-y", "-i", temp_path,
                "-filter:a", "atempo=1.25",
                file_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if os.path.exists(file_path):
                logger.info(f"[BarkTTS] Successfully saved sped-up voice track to {file_path}")
                return file_path
            else:
                logger.error("[BarkTTS] Failed to write audio file to disk.")
                return None
                
        except Exception as e:
            logger.error(f"[BarkTTS] Failed to generate voice: {e}", exc_info=True)
            return None
