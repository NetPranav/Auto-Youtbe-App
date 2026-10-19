from typing import Any, List
import re
from common import logger
from ..models import SceneData


class ScenePlanner:
    """
    Converts the final script into a detailed chronological visual timeline.
    Uses smart word-chunking to produce multiple images per sentence,
    creating fast-paced, documentary-style visual pacing (3-5s per cut).
    """
    # Target words per visual chunk. Narration at ~2.5 words/sec means
    # 10 words ≈ 4 seconds of screen time — the sweet spot for retention.
    MIN_CHUNK_WORDS = 8
    MAX_CHUNK_WORDS = 14

    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def plan_scenes(self, script: str, topic_title: str = "") -> List[SceneData]:
        """
        Generates the scene timeline using smart word-chunking.
        
        Args:
            script: The finalized narration script.
            topic_title: The topic title used to contextualize short image prompts.
        """
        logger.info("Planning scenes based on final script (smart chunking)...")

        chunks = self._smart_chunk(script)
        
        if not chunks:
            chunks = ["Did you know this tech exists?"]
        
        logger.info(f"[ScenePlanner] Script split into {len(chunks)} visual chunks "
                     f"(avg {sum(len(c.split()) for c in chunks) / len(chunks):.1f} words each)")

        # Build a short context prefix from the topic title for image prompts
        context_prefix = self._build_context_prefix(topic_title)

        # Cycle through complementary animation sequences
        animation_sequences = [
            "Slow zoom in",
            "Pan right",
            "Slow zoom out",
            "Pan left",
            "Static",       # brief pause for emphasis
            "Slow zoom in",
            "Pan left",
            "Slow zoom out",
            "Pan right",
        ]

        scenes: List[SceneData] = []
        for i, chunk in enumerate(chunks):
            # Extract meaningful keywords for the image prompt
            keywords = self._extract_keywords(chunk)
            animation = animation_sequences[i % len(animation_sequences)]

            scenes.append(
                SceneData(
                    scene_number=i + 1,
                    start_time=f"00:0{i * 4}",   # placeholder; AudioSync corrects later
                    end_time=f"00:0{(i + 1) * 4}",
                    narration_text=chunk,
                    visual_description=(
                        f"A cinematic, photorealistic documentary scene about "
                        f"{context_prefix}: {keywords}, "
                        f"dramatic lighting, shallow depth of field, 8k resolution, "
                        f"National Geographic style"
                    ),
                    animation_suggestions=animation,
                    asset_type_required="IMAGE",
                    transition_suggestion="Crossfade",
                    camera_movement="None",
                    subtitle_segment=chunk,
                )
            )
            
        # Guarantee a final scene to show the photo of the people
        scenes.append(
            SceneData(
                scene_number=len(scenes) + 1,
                start_time=f"00:0{len(scenes) * 4}", 
                end_time=f"00:0{(len(scenes) + 1) * 4}",
                narration_text="", # No narration text, just the final visual
                visual_description="A real, authentic portrait photograph of the exact people from the story, historical or modern depending on context, photorealistic",
                animation_suggestions="Static",
                asset_type_required="IMAGE",
                transition_suggestion="Crossfade",
                camera_movement="None",
                subtitle_segment="",
            )
        )

        return scenes

    # ─── Private helpers ─────────────────────────────────────────────

    def _smart_chunk(self, script: str) -> List[str]:
        """
        Split the script into word-chunks of MIN_CHUNK_WORDS–MAX_CHUNK_WORDS,
        preferring to break at natural pauses (commas, semicolons, colons,
        em-dashes, sentence endings).
        """
        # Normalise whitespace
        text = " ".join(script.replace("\n", " ").split())
        words = text.split()

        if not words:
            return []

        # Indices of words that END a natural pause (the word just before a comma, etc.)
        pause_indices = set()
        for idx, word in enumerate(words):
            if word and word[-1] in ".,;:!?—–-":
                pause_indices.add(idx)

        chunks: List[str] = []
        start = 0

        while start < len(words):
            remaining = len(words) - start

            # If the remaining words fit within MAX, just take them all
            if remaining <= self.MAX_CHUNK_WORDS:
                chunks.append(" ".join(words[start:]))
                break

            # Look for the best split point within [MIN, MAX] range
            best_end = None

            # Scan from MAX down to MIN, prefer the latest natural pause
            for end in range(
                min(start + self.MAX_CHUNK_WORDS, len(words)) - 1,
                start + self.MIN_CHUNK_WORDS - 2,
                -1,
            ):
                if end in pause_indices:
                    best_end = end + 1  # include the pause word
                    break

            # No natural pause found → hard-cut at MAX
            if best_end is None:
                best_end = start + self.MAX_CHUNK_WORDS

            chunks.append(" ".join(words[start:best_end]))
            start = best_end

        return chunks

    def _extract_keywords(self, chunk: str) -> str:
        """Pull the most visually meaningful words from a chunk for the image prompt."""
        # Strip punctuation, lowercase, take up to 8 words
        clean = re.sub(r"[^a-zA-Z0-9 ]", "", chunk)
        words = clean.split()
        # Filter out very short filler words
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "it",
            "its", "this", "that", "these", "those", "and", "but", "or",
            "not", "so", "if", "then", "than", "too", "very", "just",
        }
        keywords = [w for w in words if w.lower() not in stopwords]
        return " ".join(keywords[:8]) if keywords else " ".join(words[:8])

    def _build_context_prefix(self, topic_title: str) -> str:
        """Build a short context string from the topic title."""
        if not topic_title:
            return "the topic"
        # Take first 10 meaningful words from the title
        words = topic_title.split()[:10]
        return " ".join(words)

