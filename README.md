# Autonomous AI YouTube System

This project is an enterprise-grade autonomous YouTube automation system.

## Phase 1: Project Foundation

This repository currently contains the infrastructure foundation, including:
- Pydantic configuration management
- Centralized Loguru logging
- SQLAlchemy database connections (SQLite/PostgreSQL)
- Common utilities and abstract base interfaces
- A dependency-injected Orchestrator skeleton

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up configuration:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` if necessary.*

4. Run the health check:
   ```bash
   python main.py
   ```
