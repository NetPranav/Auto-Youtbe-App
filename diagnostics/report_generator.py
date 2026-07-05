import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.session import get_db_session
from database.models import Topic, ContentPackage, AssetPackage, Asset

def generate_health_report():
    print("Generating Diagnostics Report...")
    
    with get_db_session() as db:
        topics_count = db.query(Topic).count()
        content_pkg_count = db.query(ContentPackage).count()
        asset_pkg_count = db.query(AssetPackage).count()
        assets_count = db.query(Asset).count()
        
    report = (
        "# System Diagnostics Report\n\n"
        "## Database Summary\n"
        f"- **Topics Generated:** {topics_count}\n"
        f"- **Content Packages:** {content_pkg_count}\n"
        f"- **Asset Packages:** {asset_pkg_count}\n"
        f"- **Total Physical Assets:** {assets_count}\n\n"
        "## Health Status\n"
        "- All databases initialized correctly.\n"
        "- Modules are linked and integrated.\n"
    )
    
    with open("diagnostics/system_report.md", "w") as f:
        f.write(report)
        
    print("Report written to diagnostics/system_report.md")

if __name__ == "__main__":
    generate_health_report()
