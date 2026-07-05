# Database Architecture

The system uses SQLAlchemy ORM. For local development, SQLite is sufficient. For production, PostgreSQL is recommended.

## Core Tables

### 1. `video_projects`
The central state-tracking table.
- `id` (UUID, PK)
- `created_at` (DateTime)
- `status` (Enum: INIT, RESEARCHING, SCRIPTING, RENDERING, PUBLISHED, ERROR)
- `youtube_id` (String, nullable, populated after publish)
- `error_log` (Text, nullable)

### 2. `topics`
Tracks all generated topics to ensure we don't repeat content.
- `id` (UUID, PK)
- `project_id` (UUID, FK -> video_projects.id)
- `title` (String)
- `keywords` (String)
- `source_url` (String)
- `is_approved` (Boolean)

### 3. `scripts`
Stores the final generated scripts.
- `id` (UUID, PK)
- `project_id` (UUID, FK -> video_projects.id)
- `content_json` (JSON - structured breakdown of scenes and dialogue)
- `word_count` (Integer)
- `ai_critic_score` (Float)

### 4. `assets`
Tracks media assets used. Important for tracking hashes to avoid using the same background image in every video.
- `id` (UUID, PK)
- `project_id` (UUID, FK -> video_projects.id)
- `type` (Enum: AUDIO, IMAGE, VIDEO)
- `source` (Enum: TTS, WEB_SCRAPE, YOUTUBE_LIB)
- `file_hash` (String - to prevent duplicate usage over time)
- `local_path` (String)

### 5. `analytics_snapshots`
Populated by the Learning Engine.
- `id` (UUID, PK)
- `youtube_id` (String)
- `recorded_at` (DateTime)
- `views` (Integer)
- `watch_time_hours` (Float)
- `ctr` (Float)

## Database Workflow & State Tracking
Every time an Engine finishes a task, it returns data to the Orchestrator. The Orchestrator immediately commits this to the Database and updates the `video_projects.status`. 

If the script crashes on `RENDERING`, upon restart, the Orchestrator checks for any `video_projects` not in `PUBLISHED` or `ERROR` state, loads the assets from the DB, and resumes exactly from `RENDERING`.
