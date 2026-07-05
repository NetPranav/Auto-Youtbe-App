# Full System Workflow

This document outlines the detailed step-by-step workflow of the Orchestrator as it triggers each engine. 

## The Execution Loop (Cron Triggered: 1 Video / 3 Days)

1. **State Machine Initialization**
   - Orchestrator creates a new `VideoProject` record in the database with status `INIT`.

2. **Phase 1: Research**
   - Status -> `RESEARCHING`
   - Orchestrator calls `ResearchEngine.run()`.
   - Engine scrapes RSS feeds, Reddit, News based on `config.yml`.
   - Engine uses AI to score 10 ideas based on clickability.
   - Engine cross-references top ideas with DB to ensure no duplicate videos.
   - Engine returns winning `TopicProposal`.
   - Status -> `RESEARCH_COMPLETE`

3. **Phase 2: Content Generation**
   - Status -> `SCRIPTING`
   - Orchestrator calls `ContentEngine.run(TopicProposal)`.
   - **Draft Agent:** Writes a 1500-word script.
   - **Critic Agent:** Reviews script against predefined hooks, retention tactics, and clarity. 
   - Engine repeats Draft/Critic loop up to 3 times if quality isn't met.
   - Engine parses script into `Scene` objects (Text, visual concepts).
   - Status -> `SCRIPT_COMPLETE`

4. **Phase 3: Asset Collection**
   - Status -> `GATHERING_ASSETS`
   - Orchestrator calls `AssetEngine.run(Scenes)`.
   - Engine iterates through scenes:
     - Pulls relevant copyright-free images/video snippets from defined sources.
     - Fetches TTS audio for the script blocks.
     - Selects random non-copyrighted background music from the local YouTube audio library pool.
   - Files are saved to local temp directory mapped to the DB record.
   - Status -> `ASSETS_READY`

5. **Phase 4: Video Assembly**
   - Status -> `RENDERING`
   - Orchestrator calls `VideoEngine.run(Assets)`.
   - Engine calculates audio lengths.
   - Engine maps visual duration to audio duration.
   - Engine uses FFmpeg to stitch video + voice + background music.
   - Engine auto-generates `.srt` for captions if enabled.
   - Outputs `final_render.mp4`.
   - Status -> `RENDER_COMPLETE`

6. **Phase 5: Publishing**
   - Status -> `PUBLISHING`
   - Orchestrator calls `PublisherEngine.run(RenderedVideo)`.
   - **Thumbnail Gen:** Composites AI-generated image + bold text.
   - **SEO Gen:** AI generates Title, Description, Tags.
   - Engine connects to YouTube API.
   - Uploads via chunked protocol (handles large files and disconnects).
   - Updates DB with public `YouTube_ID`.
   - Status -> `PUBLISHED`

7. **Phase 6: Cleanup**
   - System cleans up temporary audio/visual assets to save disk space, leaving only the DB record and (optionally) the final MP4.
