# Autonomous AI YouTube System

## Project Overview
The Autonomous AI YouTube System is an enterprise-grade, fully automated media company. Its core objective is to manage the entire lifecycle of a YouTube channel without any human intervention post-setup. From ideation to publication and post-publish analytics, the system relies on AI agents to perform tasks traditionally handled by a team of researchers, scriptwriters, video editors, and social media managers.

## Mission Statement
To create a high-quality, self-sustaining content engine that autonomously produces, refines, and publishes engaging YouTube videos at a steady cadence, continuously learning and improving its outputs based on real-world viewer engagement.

## Key Capabilities
- **Autonomous Ideation:** Scrapes trends and determines viable video topics while actively avoiding duplication.
- **Self-Critiquing Script Generation:** Writes compelling scripts and automatically critiques/refines them until a high-quality threshold is met.
- **Asset Collection:** Automatically gathers copyright-safe imagery from the web and audio from the YouTube Audio Library.
- **Video Assembly:** Synthesizes voiceovers, synchronizes audio with visuals, and stitches everything into a professional final cut using FFmpeg.
- **Publishing:** Automatically generates SEO-optimized metadata and uploads the video using the YouTube Data API.
- **Feedback Loop:** Analyzes video performance post-publish to adapt future topic selection and script styles.

## Constraints & System Guardrails
- **Quality over Quantity:** Target upload frequency is 1 video every 3 days. The system should take its time to critique and polish rather than spamming.
- **Copyright Safety:** Strict avoidance of non-YouTube library music. Visual assets must be sourced from safe domains or properly generated.
- **Cost & Rate Limit Management:** Low upload frequency natively protects against API bans. Caching mechanisms will minimize redundant AI calls.
- **Resiliency:** The system is designed with rigorous `try-catch` structures. A centralized Orchestrator tracks state, ensuring that a crash at any point (e.g., rendering, uploading) can be resumed exactly where it left off, and anomalies are reported.

## Target Audience
The system itself is the "creator" and can be pointed at any niche (e.g., tech news, historical facts, educational summaries) purely through configuration parameters.
