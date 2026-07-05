# Implementation Phases

The project is strictly divided into the following phases. A phase must be completed, tested, and documented before moving to the next.

## Phase 1: Project Foundation
- **Objective:** Establish the core infrastructure, database, and configuration.
- **Inputs:** Environment variables.
- **Outputs:** Working DB connection, initialized schema, active logging system.
- **Dependencies:** None.

## Phase 2: Research Engine
- **Objective:** Autonomously identify the best video topic.
- **Inputs:** RSS feeds, target keywords, current DB state (to avoid dupes).
- **Outputs:** `TopicProposal` object saved to DB.
- **Dependencies:** Core DB, LLM Provider.

## Phase 3: Content Engine
- **Objective:** Turn a topic into a highly engaging, self-critiqued script.
- **Inputs:** `TopicProposal`.
- **Outputs:** `VideoScript` object, `ScenePlan`.
- **Dependencies:** LLM Provider.

## Phase 4: Asset Engine
- **Objective:** Gather all raw media needed to visualize the script.
- **Inputs:** `ScenePlan`.
- **Outputs:** Folder of downloaded/generated media files (Audio, Images).
- **Dependencies:** TTS Provider, Web/Image Fetcher, YouTube Audio Library pool.

## Phase 5: Video Engine
- **Objective:** Assemble assets into a professional final video.
- **Inputs:** Media folder, `VideoScript` timing data.
- **Outputs:** Final `output.mp4` and `thumbnail.jpg`.
- **Dependencies:** FFmpeg installed on host machine.

## Phase 6: Publishing Engine
- **Objective:** Upload the video to YouTube with SEO metadata.
- **Inputs:** Final `output.mp4`, `TopicProposal` context.
- **Outputs:** YouTube Video URL, Upload Status.
- **Dependencies:** YouTube Data API v3.

## Phase 7: Learning Engine
- **Objective:** Analyze past performance to adjust future content.
- **Inputs:** Published Video IDs.
- **Outputs:** Strategy/Prompt adjustments for Research and Content engines.
- **Dependencies:** YouTube Analytics API.

## Phase 8: The Orchestrator
- **Objective:** Tie all engines together into an autonomous loop with crash recovery.
- **Inputs:** Cron trigger.
- **Outputs:** Full pipeline execution from Phase 2 to Phase 7.
- **Dependencies:** All previous phases.
