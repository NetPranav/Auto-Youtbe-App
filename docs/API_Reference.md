# API Reference

This document outlines the internal programmatic APIs for the major components of the system.

## ProviderManager
`providers.manager.ProviderManager`
Manages the instantiation of AI providers based on `.env` settings.
- `get_provider(engine_context: str) -> BaseProvider`: Returns the appropriate provider (e.g. `nim` or `deepseek`) configured for the requested context (e.g., `research`, `content`).

## BaseProvider
`providers.base.BaseProvider`
Abstract base class for all AI implementations.
- `generate_text(prompt: str, max_tokens: int = 1000) -> str`: Executes an LLM prompt.
- `generate_image(prompt: str, output_path: str) -> str`: Generates an image and saves it to disk.

## VideoEngine
`video_engine.engine.VideoEngine`
Orchestrates the FFmpeg rendering pipeline.
- `run(asset_package_id: str) -> Optional[str]`: Fetches assets, builds a timeline, renders the video, and returns the absolute path to the `.mp4`.

## PublishingEngine
`publisher.engine.PublishingEngine`
Automated metadata and upload handler.
- `run(project_id: str) -> Optional[str]`: Generates SEO metadata, selects a thumbnail, uploads to the platform, and returns the live video URL.

## LearningEngine
`learning_engine.engine.LearningEngine`
The self-improving brain of the system.
- `run() -> None`: Fetches recent published videos, queries analytics, runs 5 specialized analyzers, and dumps a new `data/strategy.json` configuration file.
