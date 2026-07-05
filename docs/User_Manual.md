# User Manual

Welcome to the Auto-Youtube-App! This tool allows you to automatically generate, edit, and publish YouTube videos 24/7 without manual intervention.

## 1. Initial Configuration
Before running the app, you must set up your environment variables:
1. Rename `.env.example` to `.env`.
2. Provide your API keys (e.g., `NVIDIA_API_KEY`).
3. Set your target niche in `config/settings.py` (e.g., `youtube_default_category_id`).

## 2. Generating a Video
To run the complete pipeline from Idea to Published Video:
```bash
python integration/run_full_pipeline.py
```
This script will:
1. Research a trending topic.
2. Write a highly-retaining script.
3. Generate AI voiceovers and images.
4. Render the video using FFmpeg.
5. Upload the video to YouTube.

## 3. Reviewing Outputs
If you want to review the outputs before publishing:
1. Navigate to the `data/rendered_videos/` directory to view the final `.mp4`.
2. Navigate to `data/assets/` to view the individual images, audio files, and `.srt` subtitles.

## 4. Enabling the Learning Engine
The system gets smarter over time. To analyze your published videos and generate a new strategy profile:
```bash
python integration/run_learning_pipeline.py
```
This will read the analytics, score the performance, and automatically modify the prompts for future videos to maximize views and retention!
