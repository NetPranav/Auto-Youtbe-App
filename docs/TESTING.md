# Testing Strategy

An autonomous system modifying external state (uploading videos) requires robust testing to prevent runaway costs or publishing garbage to a public channel.

## Unit Testing
We will use `pytest` for all engines. Each engine's tests should be fully mocked so they do not hit real APIs.
- **Mocking LLMs:** The `BaseLLMProvider` will have a `MockProvider` implementation that returns hardcoded JSON responses to test the parsing logic of the Content and Research engines.
- **Mocking Filesystem:** Video Engine tests will use tiny 1-second blank video/audio clips to verify FFmpeg stitches files correctly without needing to render a 10-minute 4k video.

## Integration Testing
- The Orchestrator will be tested using a local SQLite database and mock API responses.
- We will verify that state transitions (INIT -> RESEARCHING -> SCRIPTING) occur properly and that errors trigger the `error_log` field in the database rather than crashing the script.

## Dry-Run Mode
The system will implement a `DRY_RUN=True` environment variable. 
When true:
- Videos are generated and saved locally, but the `Publisher` engine skips the YouTube API upload step.
- AI Agents are still called, but the system halts at the very end.

This is the primary way the developer will test the entire pipeline locally.

## CI/CD Strategy
- GitHub Actions (or similar) will run the `pytest` suite on every commit.
- A linting step (`ruff` or `flake8`) will enforce code style.
