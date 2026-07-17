#!/bin/bash
set -e

echo "======================================"
echo "Cleaning up old data..."
echo "======================================"
rm -f yt_automate.db
rm -rf assets/*
rm -rf test_Case/asset_engine/asset_output.json

echo "======================================"
echo "Phase 1 & 2: Research Engine"
echo "======================================"
python test_research.py

echo "======================================"
echo "Phase 3: Content Engine"
echo "======================================"
python test_Case/content_engine/test_content.py

echo "======================================"
echo "Phase 4: Asset Engine"
echo "======================================"
python test_Case/asset_engine/test_asset.py

echo "======================================"
echo "Phase 5: Video Engine"
echo "======================================"
python test_Case/video_engine/test_video.py

echo "======================================"
echo "ALL PHASES COMPLETE!"
echo "Your video is ready in assets/renders/"
echo "======================================"
