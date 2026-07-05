# Deployment Guide

This guide covers deploying the application to a headless server or cloud instance (e.g., AWS EC2, DigitalOcean Droplet) for 24/7 autonomous generation.

## Prerequisites
- Ubuntu 22.04 LTS (Recommended)
- Python 3.10+
- FFmpeg
- At least 4GB RAM (If relying strictly on remote APIs for generation)

## Installation Steps
```bash
sudo apt update
sudo apt install python3-pip python3-venv ffmpeg -y

git clone https://github.com/NetPranav/Auto-Youtbe-App.git
cd Auto-Youtbe-App

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running as a Background Service
To ensure the pipeline runs continuously and survives server reboots, configure a `systemd` service or a `cron` job.

### Example Cron Job (Runs every 12 hours)
```bash
crontab -e
# Add the following line:
0 */12 * * * cd /path/to/Auto-Youtbe-App && /path/to/Auto-Youtbe-App/venv/bin/python integration/run_full_pipeline.py >> /var/log/yt_automate.log 2>&1
```

## YouTube Authentication on a Headless Server
Because the YouTube Data API uses OAuth2 requiring a browser redirect:
1. Run the script locally on your Desktop first to authenticate via the browser.
2. This generates a `token.json` file.
3. Securely transfer `client_secret.json` and `token.json` to your server.
4. The Publisher Engine will load the existing token and refresh it automatically without requiring a browser.
