# Handover Document: Auto-Youtube Pipeline (Windows Migration)

**To the AI Assistant resuming this project:**
The user has just migrated this codebase from a MacBook to a Windows laptop (RTX 4060 8GB VRAM, 16GB RAM) to take advantage of CUDA acceleration. 

Please read this document carefully to understand the current state of the architecture, recent major changes, and the immediate next steps.

---

## 1. Recent Architectural Pivot (Current Affairs)
We recently overhauled the **Research Engine (v2)**. The user pivoted the channel's focus from "History Documentaries" to an **Investigative Current Affairs System**. The engine is now designed to investigate ongoing societal issues (e.g., Water Scarcity, Global Cybercrime, Infrastructure Failures).
- **Strict Neutrality:** The multi-agent debate system (Investigative Journalist, Data Analyst, Neutrality Enforcer) strictly forbids political bias, blame, or speculation. It is purely fact-driven and educational.

## 2. Deep Research Data Model
The `TopicCandidate` (and SQLite database schema) was updated. It no longer uses fields like `main_technology` or `estimated_audience`. Instead, it extracts exactly 7 deep research questions:
1. `problem_definition`
2. `historical_comparison`
3. `root_cause_analysis`
4. `supporting_evidence`
5. `counterarguments`
6. `global_comparison`
7. `practical_solutions`

## 3. Strict 9.0 Confidence Threshold
The `TopicRanker` now strictly enforces a `9.0 / 10.0` minimum score to approve a topic. 
- The score is calculated as the average of 6 positive metrics + a `safety_score` (which is `10.0 - conflict_risk`).
- **Test Environment Mocks:** Because the 9.0 threshold is very hard to hit when using small LLMs, the mock data in `research_engine/source_connectors/rss.py` and `hackernews.py` has been explicitly engineered with "perfect" verifiable articles to guarantee a passing score during offline testing.

## 4. Alternating Topic Categories
The engine now features **Stateful Category Alternation**. 
- The `Topic` table now records `category_type` (e.g., `CURRENT_AFFAIRS` or `HISTORY`).
- Every time the `ResearchEngine` runs, it checks the database for the last approved topic's category. If the last topic was `CURRENT_AFFAIRS`, it will instruct the AI prompts and data collectors to specifically hunt for `HISTORY` (e.g., WW2, 1800-2000s masterminds), and vice versa. 
- This guarantees the channel naturally toggles between high-tier historical documentaries and current investigative reports to match the photo editing aesthetic.

## 5. Immediate Next Step: The Bark Voice Engine
The user wants to replace the current `edge_tts` voice provider with **Bark** (by Suno) to generate highly realistic, emotional voiceovers natively offline.
- Because the user now has an RTX 4060 with 8GB VRAM, Bark will run beautifully.
- **Implementation requirement:** When you build the Bark provider (`providers/voice/bark.py`), you **MUST** enable `SUNO_OFFLOAD_CPU=True` (or the equivalent environment variable) so that the models swap seamlessly between the 8GB VRAM and 16GB System RAM to prevent out-of-memory errors.
- **Dependencies:** You will need to help the user install PyTorch with CUDA support for Windows, along with the `suno-bark` library.

---

**End of Handover.** 
*You can delete this file once you have successfully set up Bark and confirmed the pipeline is working on Windows!*
