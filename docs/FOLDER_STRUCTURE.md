# Folder Structure Overview

This project uses a standard Python Modular Monolith structure.

```text
a:/Project Folder/yt automate/
├── config/
│   ├── __init__.py
│   ├── settings.py           # Pydantic BaseSettings class
│   └── prompts.yaml          # Externalized LLM prompts
├── common/
│   ├── __init__.py
│   ├── logger.py             # Loguru setup
│   └── exceptions.py         # Custom error classes (e.g., RecoverableError)
├── database/
│   ├── __init__.py
│   ├── models.py             # SQLAlchemy ORM classes
│   └── db.py                 # Engine and SessionLocal setup
├── docs/                     # Architectural documentation (this folder)
├── logs/                     # JSON log files generated at runtime
├── tests/
│   ├── test_orchestrator/
│   ├── test_research/
│   └── ...
├── orchestrator/
│   ├── __init__.py
│   └── state_machine.py      # The main execution loop
├── research_engine/
│   ├── __init__.py
│   ├── scraper.py            # Web scraping logic
│   └── analyzer.py           # LLM topic selection
├── content_engine/
│   ├── __init__.py
│   ├── writer_agent.py
│   ├── critic_agent.py
│   └── scene_planner.py
├── asset_engine/
│   ├── __init__.py
│   ├── image_fetcher.py
│   ├── tts_generator.py
│   └── local_audio_lib.py    # Interfaces with locally stored YT Audio Lib
├── video_engine/
│   ├── __init__.py
│   ├── timeline.py           # Sync logic
│   └── renderer.py           # FFmpeg subprocess wrappers
├── publisher/
│   ├── __init__.py
│   ├── youtube_api.py        # OAuth and Upload logic
│   └── metadata_gen.py       # SEO Title/Tag gen
└── learning_engine/
    ├── __init__.py
    └── analytics.py          # Fetches stats to update DB weights
```

**Why this structure?**
It strictly enforces separation of concerns. The `video_engine` knows nothing about how a script is generated; it only accepts an asset folder and timing JSON. The `orchestrator` manages the data passing between these distinct modules.
