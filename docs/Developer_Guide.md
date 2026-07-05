# Developer Guide

Welcome to the Auto-Youtube-App repository. This document explains how to set up the development environment, extend the engines, and write new AI Provider implementations.

## Local Setup
1. Clone the repository: `git clone https://github.com/NetPranav/Auto-Youtbe-App.git`
2. Create a virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your API keys (specifically `NVIDIA_API_KEY`).
5. Ensure `ffmpeg` is installed on your OS and available in your system `PATH`.

## Adding a New AI Provider
If you want to swap out NVIDIA Build (NIM) for OpenAI or Anthropic:
1. Navigate to `providers/llm/`.
2. Create a new file (e.g., `openai_provider.py`).
3. Inherit from `BaseProvider` located in `providers/base.py`.
4. Implement the `generate_text` and `generate_image` methods.
5. Update `providers/manager.py` to register your new provider class based on the environment variables.

## Adding a New Rendering Preset
The Video Engine allows configurable styles.
1. Navigate to `video_engine/presets/`.
2. Create a new JSON file (e.g., `tech_review.json`).
3. Define the target resolutions, default transition types, and motion intensities.
4. Pass the preset name into the `TimelineBuilder` inside `video_engine/engine.py`.
