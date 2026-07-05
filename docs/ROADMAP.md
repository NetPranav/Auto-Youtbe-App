# Development Roadmap

This roadmap outlines the progression of the Autonomous AI YouTube System from its foundational setup to full autonomy.

## Phase 1: Project Foundation (Current)
- [x] Gather requirements and constraints.
- [x] Design modular architecture.
- [x] Generate system documentation.
- [x] Setup folder structure.
- [ ] Initialize Python environment (virtualenv).
- [ ] Setup base configuration management (Pydantic).
- [ ] Setup database models (SQLAlchemy) and Alembic migrations.
- [ ] Implement central logging.

## Phase 2: Research Engine
- [ ] Implement abstract scrapers (Web, RSS, Reddit).
- [ ] Implement LLM integration for topic analysis.
- [ ] Develop database check for topic deduplication.
- [ ] Write tests for Research Engine.

## Phase 3: Content Engine
- [ ] Develop multi-agent script generation (Writer vs. Critic).
- [ ] Implement scene breakdown logic (mapping script lines to visual concepts).
- [ ] Write tests for script formatting and quality thresholds.

## Phase 4: Asset Engine
- [ ] Integrate text-to-speech (TTS) provider.
- [ ] Develop web image scraper/fetcher with copyright safety rules.
- [ ] Setup local YouTube Audio Library integration.
- [ ] Implement asset tracking to avoid reuse of images.

## Phase 5: Video Engine
- [ ] Develop FFmpeg wrapper for timeline assembly.
- [ ] Implement audio ducking (lowering music during voiceover).
- [ ] Implement subtitle generation (.srt / hardcoded).
- [ ] Write rendering tests (checking for valid output file).

## Phase 6: Publishing Engine
- [ ] Setup Google Cloud Console / YouTube Data API credentials.
- [ ] Implement LLM-based SEO metadata generation.
- [ ] Develop resumable chunked video uploader.
- [ ] Implement thumbnail generator (compositing text over background).

## Phase 7: Orchestrator & State Management
- [ ] Build the central state machine.
- [ ] Implement database checkpointing and crash recovery logic.
- [ ] Develop top-level try-catch and notification system.

## Phase 8: Learning Engine (Post-Launch)
- [ ] Implement YouTube Analytics API fetcher.
- [ ] Develop LLM analysis of performance metrics (CTR, retention).
- [ ] Feed insights back into Research and Content engine prompts.

## Phase 9: Optimization & Deployment
- [ ] Dockerize the application.
- [ ] Setup cron/scheduling for the "1 video per 3 days" cadence.
- [ ] Implement automated cleanup of old raw assets.
