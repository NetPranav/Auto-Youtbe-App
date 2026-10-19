import uuid
import os
import re
from typing import Optional
from common import logger


class SubtitleGenerator:
    """
    Generates properly-timed SRT subtitle files from a script.
    Splits the text into short, readable chunks and distributes
    timestamps evenly across the estimated narration duration.
    """
    # Average narration speed in words-per-second
    WORDS_PER_SECOND = 2.5
    # Target words per subtitle block (sweet spot for fast, punchy Shorts captions)
    WORDS_PER_BLOCK = 3

    def generate(self, text: str, storage_dir: str) -> Optional[str]:
        logger.info("Generating subtitle track...")

        file_name = f"subtitles_{uuid.uuid4().hex[:8]}.srt"
        output_path = os.path.join(storage_dir, file_name)
        os.makedirs(storage_dir, exist_ok=True)

        blocks = self._build_srt_blocks(text)

        if not blocks:
            logger.warning("[SubtitleGenerator] No subtitle blocks generated.")
            return None

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(blocks)
            logger.info(f"[SubtitleGenerator] Wrote {blocks.count(chr(10) + chr(10))+1} subtitle blocks to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save subtitles: {e}")
            return None

    def _build_srt_blocks(self, text: str) -> str:
        """Split text into timed SRT blocks."""
        # Normalise whitespace
        text = " ".join(text.replace("\n", " ").split())
        words = text.split()

        if not words:
            return ""

        total_duration = len(words) / self.WORDS_PER_SECOND
        chunks = self._chunk_words(words)
        chunk_count = len(chunks)

        # Distribute time evenly across chunks
        time_per_chunk = total_duration / chunk_count if chunk_count else 1.0

        srt_parts = []
        for i, chunk_text in enumerate(chunks):
            start_sec = i * time_per_chunk
            end_sec = (i + 1) * time_per_chunk
            srt_parts.append(
                f"{i + 1}\n"
                f"{self._format_ts(start_sec)} --> {self._format_ts(end_sec)}\n"
                f"{chunk_text}\n"
            )

        return "\n".join(srt_parts)

    def _chunk_words(self, words: list) -> list:
        """Group words into subtitle-sized chunks, preferring natural pauses."""
        chunks = []
        i = 0
        while i < len(words):
            end = min(i + self.WORDS_PER_BLOCK, len(words))

            # Try to extend or shrink by 1-2 words to land on punctuation
            best = end
            for offset in range(0, 3):
                check = end + offset
                if check <= len(words) and check > i:
                    last_word = words[check - 1]
                    if last_word and last_word[-1] in ".,;:!?—–-":
                        best = check
                        break

            chunk_text = " ".join(words[i:best])
            chunks.append(chunk_text)
            i = best

        return chunks

    @staticmethod
    def _format_ts(seconds: float) -> str:
        """Convert seconds to SRT timestamp format HH:MM:SS,mmm."""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

