# System Architecture

The Auto-YouTube-App is designed as a fully modular, 7-phase pipeline. Each phase operates as an independent "Engine" that receives structured input, executes an autonomous workflow using an abstract AI Provider layer, and produces a concrete artifact (database row or file).

## The 7 Engines

1. **Foundation (Config & Providers)**: The abstraction layer. No engine talks directly to an API. They query the `ProviderManager`, allowing LLMs to be hot-swapped dynamically without breaking business logic.
2. **Research Engine**: Takes a broad topic, scrapes the web or queries an LLM to extract trending angles, and produces a structured `ResearchPackage`.
3. **Content Engine**: Transforms research into a highly engaging, structured `Script` with visual cues and scene boundaries.
4. **Asset Engine**: Reads the script and generates all required raw assets: TTS Voiceovers, AI Images, and basic Subtitle `.srt` files.
5. **Video Engine**: The mathematical timeline builder. It translates the assets into programmatic FFmpeg filter graphs to generate a final, fully rendered `.mp4`.
6. **Publishing Engine**: The automated Channel Manager. Generates high-CTR SEO metadata, validates file constraints, schedules, and uploads via the YouTube Data API.
7. **Learning Engine**: The Chief Strategy Officer. Analyzes historical performance (Views, Retention, CTR), updates global strategy profiles (`data/strategy.json`), and feeds improved prompts back into the pipeline.

## Database Schema
The system uses SQLite via SQLAlchemy. The central node is the `ContentPackage`, which ties together Research, Assets, and Video Projects to maintain strict relational integrity across engine restarts.
