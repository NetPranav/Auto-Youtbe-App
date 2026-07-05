# Project TODO List

This document holds minor fixes, refactoring ideas, and loose ends that don't belong in the main roadmap.

## Pending Tasks (Phase 1 Follow-ups)
- [ ] Setup `requirements.txt` or `pyproject.toml` with the recommended libraries (`ffmpeg-python`, `sqlalchemy`, `litellm`, etc).
- [ ] Create `.gitignore` to ensure `logs/` and `__pycache__` and local media assets are not committed.
- [ ] Set up a `.env.example` file so the user knows exactly which API keys are required (e.g., OPENAI_API_KEY, YOUTUBE_CLIENT_ID).

## Future Ideas / Backlog
- Create a simple web dashboard (FastAPI + React) to visualize the DB state of the orchestrator so the user can see what the AI is currently doing without reading terminal logs.
- Add support for YouTube Shorts generation alongside long-form videos by branching the `VideoEngine` rendering resolution to 1080x1920.
