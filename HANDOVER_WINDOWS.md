# Handover Document: Auto-Youtube Pipeline (Windows Migration)

**To the AI Assistant resuming this project:**
The user has just migrated this entire codebase from a MacBook (Mac OS) to a Windows laptop. 
**Why this migration happened:** The Mac lacked the dedicated GPU hardware required for heavy AI workloads. The new Windows machine is equipped with an **NVIDIA RTX 4060 (8GB VRAM) and 16GB RAM**. This hardware upgrade allows the project to utilize **CUDA acceleration** to run advanced local AI models natively and offline—most importantly, the highly realistic **Bark voice engine** which is far superior to standard API-based TTS like `edge_tts`.

Please read this document carefully to understand the current state of the architecture, recent major changes, and the exact steps you need to take next.

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

## 5. Explicit Instructions for the New AI (What you must do next)
Your immediate priority is to harness the new RTX 4060 GPU to upgrade the Voice Generation phase.

**Step 1: Environment Setup**
You must help the user set up a CUDA-enabled Python environment on their new Windows machine. Ensure they install PyTorch with CUDA support and the `suno-bark` library.

**Step 2: Implement the Bark Provider**
The user wants to replace the current `edge_tts` voice provider with **Bark** (by Suno) to generate highly realistic, emotional voiceovers natively offline without relying on paid APIs.
- Create `providers/voice/bark.py`.
- **CRITICAL Implementation requirement:** You **MUST** enable `SUNO_OFFLOAD_CPU=True` (or the equivalent environment variable) in the Bark implementation. The RTX 4060 has 8GB VRAM, but Bark can easily exceed this. This setting ensures the models swap seamlessly between the 8GB VRAM and 16GB System RAM to prevent out-of-memory crashes.

**Step 3: Fix Video/Subtitle Output Quality**
Once Bark is running successfully, the user has noted that they want you to "fix the output properly"—specifically referring to the final video output and subtitles which are not yet at the desired premium quality level. 

---

---

**End of Handover.** 
*You can delete this file once you have successfully set up Bark and confirmed the pipeline is working on Windows!*
