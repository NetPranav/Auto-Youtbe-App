import os
import sys

# Ensure the root directory is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from loguru import logger
from database.session import get_db_session
from database.models import Topic
from content_engine.engine import ContentEngine
from config import config

def main():
    logger.info("Starting Content Engine Test...")
    
    topic_id = None
    with get_db_session() as db:
        # Find the latest approved topic
        topic = db.query(Topic).filter(Topic.is_approved == True).first()
        
        if not topic:
            logger.error("No approved topics found in the database. Run test_research.py on fresh data first to generate one!")
            return
            
        topic_id = topic.id
        logger.info(f"Found approved topic: '{topic.title}' (ID: {topic_id})")

        logger.info("Initializing Content Engine. Get ready to see the AI Writer's Room in action!")
        engine = ContentEngine(db_session=db)
        result = engine.run(topic_id)
    
    if result:
        logger.success("Content Engine generated a full package!")
        
        # === SAVE DEBUG SCRIPT ===
        debug_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets")
        os.makedirs(debug_dir, exist_ok=True)
        debug_script_path = os.path.join(debug_dir, "debug_script.txt")
        with open(debug_script_path, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("FULL GENERATED SCRIPT (DEBUG OUTPUT)\n")
            f.write("=" * 80 + "\n\n")
            f.write(result.final_script or "N/A")
            f.write("\n\n")
            f.write("=" * 80 + "\n")
            f.write(f"SCENES GENERATED: {len(result.scene_timeline)}\n")
            f.write("=" * 80 + "\n")
            for scene in result.scene_timeline:
                f.write(f"\nScene {scene.scene_number}:\n")
                f.write(f"  Narration: {scene.narration_text}\n")
                f.write(f"  Visual: {scene.visual_description}\n")
        logger.success(f"Debug script saved to: {debug_script_path}")
        
        print("\n" + "="*80)
        print("THE CONTENT STRATEGY")
        print("="*80)
        if result.strategy:
            print(f"Target Audience: {result.strategy.target_audience}")
            print(f"Tone: {result.strategy.tone}")
            print(f"Objective: {result.strategy.objective}")
            print(f"Curiosity Level: {result.strategy.curiosity_level}")
        
        print("\n" + "="*80)
        print("THE WINNING HOOK (First 10 seconds)")
        print("="*80)
        if result.winning_hook:
            print(f"Hook Text: {result.winning_hook.text}")
            print(f"Hook Score: {result.winning_hook.score}")

        print("\n" + "="*80)
        print("THE SCRIPT OUTLINE")
        print("="*80)
        if result.outline:
            for i, section in enumerate(result.outline):
                print(f"{i+1}. {section}")
        
        print("\n" + "="*80)
        print("FINAL SCRIPT PREVIEW (First 1000 characters)")
        print("="*80)
        print(result.final_script[:1000] if result.final_script else "N/A")
        print("...\n")
        
        print("\n" + "="*80)
        print("SCENE TIMELINE PREVIEW (First 3 scenes)")
        print("="*80)
        for scene in result.scene_timeline[:3]:
            print(f"Scene {scene.scene_number} [{scene.start_time} - {scene.end_time}]")
            print(f"Visual Idea: {scene.visual_description}")
            print(f"Asset Needed: {scene.asset_type_required}")
            print(f"Voiceover: {scene.narration_text}\n")
            
        print("="*80)
        print("FINAL QUALITY SCORES (After Optimization Loop)")
        print("="*80)
        if result.scores:
            print(f"Fact Check Score: {result.scores.fact_score} / 1.0")
            print(f"Viewer Retention Score: {result.scores.retention_score} / 1.0")
            print(f"Overall Script Quality: {result.scores.script_quality_score} / 1.0")
            print("\nFinal Feedback Notes from the Critic AI:")
            for note in result.scores.feedback_notes:
                print(f"- {note}")
            
    else:
        logger.warning("Content Engine finished but failed to generate a package.")

if __name__ == "__main__":
    main()
