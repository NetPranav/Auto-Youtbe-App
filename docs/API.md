# External API Integration Plan

The system relies on a few critical external APIs. To prevent vendor lock-in, all APIs are wrapped in local interfaces.

## 1. YouTube Data API v3
**Purpose:** Uploading videos, setting thumbnails, updating metadata.
**Authentication:** OAuth2 (Requires initial manual consent, then relies on refresh tokens).
**Rate Limits:** 10,000 quota units per day. (A video upload costs ~1,600 units). 
**Strategy:** At 1 video per 3 days, quota exhaustion is impossible.

## 2. YouTube Analytics API
**Purpose:** Fetching performance metrics (CTR, Watch Time).
**Authentication:** Same OAuth2 credentials as Data API.
**Strategy:** Queried once a day by the Learning Engine for recent videos.

## 3. LLM API (OpenAI / Anthropic / Local)
**Purpose:** Topic selection, script writing, critic evaluation, SEO generation.
**Authentication:** API Key (or localhost for Ollama).
**Strategy:** All calls go through an abstraction layer. If OpenAI is down, it seamlessly falls back to another provider defined in `config.yml`.

## 4. Text-to-Speech (TTS) API
**Purpose:** Generating voiceovers.
**Options:** ElevenLabs (High quality, expensive), Edge TTS (Free, decent quality), OpenAI TTS.
**Strategy:** TTS is heavily cached. If a script segment doesn't change during regeneration, the previously downloaded audio file is reused to save API costs.

## 5. Web Scraping & Image APIs
**Purpose:** Gathering visual assets.
**Options:** Unsplash API, Pexels API, or direct headless browser scraping using Playwright.
**Strategy:** Strictly adhere to copyright-free filters. If an API hits a rate limit, the system pauses the `AssetEngine` and schedules a retry in 1 hour.
