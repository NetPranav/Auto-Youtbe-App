# Error Handling & Resiliency Strategy

Because this is a completely autonomous system designed to run without humans, it must not crash silently.

## 1. Global Try-Catch (The Orchestrator)
Every Engine is wrapped in a top-level try-catch within the Orchestrator loop.

```python
try:
    video_engine.run(project_id)
except Exception as e:
    orchestrator.mark_error(project_id, e)
    orchestrator.notify_admin(f"CRITICAL: Rendering failed. {e}")
```

## 2. API Retries (Exponential Backoff)
Network calls fail. If the YouTube API or an AI provider returns a 500 or 429 (Rate Limit), the system utilizes the `tenacity` library to retry.

- **Attempt 1:** Wait 5 seconds.
- **Attempt 2:** Wait 30 seconds.
- **Attempt 3:** Wait 5 minutes.
- **Attempt 4:** Fail and trigger Global Try-Catch.

## 3. Idempotency (State-Based Resumption)
If power goes out and the server restarts, the Orchestrator boots up and queries the DB:
`SELECT * FROM video_projects WHERE status NOT IN ('PUBLISHED', 'ERROR')`
If it finds a project stuck in `ASSETS_READY`, it skips the Research, Script, and Asset phases, loading the state from DB and immediately passing it to the Video Engine. 

## 4. Self-Healing AI Troubleshooting
If an error is textual and understandable (e.g., "Script generated is too short"), the Orchestrator can feed the error back to the LLM. 
*Example:* "The video assembly failed because Scene 4 has no audio. Please rewrite the JSON scene mapping."
*Limit:* Self-healing will only attempt twice before escalating to the human admin to prevent endless infinite loops.

## 5. Fallback Mechanisms
- If Web Scraper API fails -> Fallback to searching Wikipedia text-only.
- If TTS provider fails -> Fallback to a secondary provider (e.g., Edge TTS).
- If YouTube Upload fails -> Save the `.mp4` locally and retry in 24 hours.
