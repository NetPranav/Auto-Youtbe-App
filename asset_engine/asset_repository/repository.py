from typing import List, Any
from common.interfaces import BaseRepository
from database.session import get_db_session
from database.models import AssetPackage, Asset, AssetValidation

class AssetRepository(BaseRepository):
    """
    Handles DB CRUD for the Asset Engine.
    """
    def create_package(self, content_package_id: str) -> str:
        with get_db_session() as db:
            pkg = AssetPackage(content_package_id=content_package_id)
            db.add(pkg)
            db.flush()
            return pkg.id

    def save_asset(self, package_id: str, scene_id: str, asset_type: str, provider: str, file_path: str) -> str:
        with get_db_session() as db:
            a = Asset(
                package_id=package_id,
                scene_id=scene_id if scene_id != "global" else None,
                asset_type=asset_type,
                provider=provider,
                file_path=file_path
            )
            db.add(a)
            db.flush()
            return a.id

    def save_validation(self, asset_id: str, status: str, report: dict) -> None:
        with get_db_session() as db:
            v = AssetValidation(
                asset_id=asset_id,
                status=status,
                report_json=report
            )
            db.add(v)

    def complete_package(self, package_id: str, status: str = "FINALIZED") -> None:
        with get_db_session() as db:
            pkg = db.query(AssetPackage).filter(AssetPackage.id == package_id).first()
            if pkg:
                pkg.status = status
