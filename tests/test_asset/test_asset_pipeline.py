import pytest
import os
import shutil
from database.models import Scene
from asset_engine.asset_analyzer.analyzer import AssetAnalyzer
from asset_engine.asset_planner.planner import AssetPlanner
from asset_engine.image_generator.generator import ImageGenerator
from asset_engine.asset_validator.validator import AssetValidator

def test_asset_analyzer():
    analyzer = AssetAnalyzer()
    
    # Mock scenes
    scene1 = Scene(id="s1", asset_type_required="IMAGE", visual_description="A Python logo.")
    scene2 = Scene(id="s2", asset_type_required="IMAGE", visual_description="A man coding at a desk.")
    scene3 = Scene(id="s3", asset_type_required="VIDEO", visual_description="Abstract tech background.")
    
    reqs = analyzer.analyze([scene1, scene2, scene3])
    
    assert len(reqs) == 3
    
    # Scene 1 should detect logo -> FETCHED_IMAGE
    assert reqs[0]["visuals"][0]["type"] == "FETCHED_IMAGE"
    
    # Scene 2 should be AI_IMAGE
    assert reqs[1]["visuals"][0]["type"] == "AI_IMAGE"
    
    # Scene 3 should be STOCK_VIDEO
    assert reqs[2]["visuals"][0]["type"] == "STOCK_VIDEO"

def test_asset_planner():
    planner = AssetPlanner()
    analyzed = [
        {"scene_id": "s1", "visuals": [{"type": "AI_IMAGE", "query": "man coding"}]}
    ]
    
    # Plan includes global voice, subtitle, and the s1 image
    plan = planner.plan_assets(analyzed, "Test script")
    assert len(plan) == 3
    assert plan[0].asset_type == "VOICE"
    assert plan[1].asset_type == "SUBTITLE"
    assert plan[2].asset_type == "IMAGE"
    assert plan[2].scene_id == "s1"

def test_generators_and_validation():
    storage_dir = "tests/test_assets_out"
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)
        
    generator = ImageGenerator()
    file_path = generator.generate("mock", "Test prompt", storage_dir)
    
    assert file_path is not None
    assert os.path.exists(file_path)
    
    validator = AssetValidator()
    val_res = validator.validate(file_path, "IMAGE")
    
    assert val_res["status"] == "PASSED"
    assert val_res["report"]["file_exists"] is True
    
    # Cleanup
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)
