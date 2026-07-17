import os
import sys
import json
from loguru import logger

# Ensure the root directory is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.session import get_db_session
from database.models import ContentPackage
from asset_engine.engine import AssetEngine
from config import config

def main():
    logger.info("Starting Asset Engine Test...")
    
    pkg_id = None
    with get_db_session() as db:
        # Find the latest finalized content package
        pkg = db.query(ContentPackage).filter(ContentPackage.status == "FINALIZED").order_by(ContentPackage.created_at.desc()).first()
        
        if not pkg:
            logger.error("No FINALIZED ContentPackage found. Run the Content Engine first!")
            return
            
        pkg_id = pkg.id
        logger.info(f"Found ContentPackage ID: {pkg_id}")

    logger.info("Initializing Asset Engine...")
    engine = AssetEngine()
    result = engine.run(pkg_id)
    
    if result:
        logger.success("Asset Engine finished successfully!")
        
        # Serialize the output for the user
        output_data = {
            "content_package_id": result.content_package_id,
            "assets_generated": []
        }
        
        for asset in result.assets:
            output_data["assets_generated"].append({
                "asset_type": asset.request.asset_type if asset.request else "UNKNOWN",
                "provider_type": asset.request.provider_type if asset.request else "UNKNOWN",
                "file_path": asset.file_path,
                "status": asset.status,
                "metadata": asset.metadata
            })
            
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asset_output.json")
        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=4)
            
        logger.success(f"Saved complete asset output to {output_file}")
        
    else:
        logger.warning("Asset Engine finished but failed to generate assets.")

if __name__ == "__main__":
    main()
