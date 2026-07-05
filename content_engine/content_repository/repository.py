from typing import Any, List, Dict
from common.interfaces import BaseRepository
from database.session import get_db_session
from database.models import ContentPackage, Hook, Outline, Script, ScriptRevision, Scene

class ContentRepository(BaseRepository):
    """
    Handles DB CRUD for the Content Engine.
    """

    def create_package(self, topic_id: str) -> str:
        with get_db_session() as db:
            pkg = ContentPackage(topic_id=topic_id)
            db.add(pkg)
            db.flush()
            return pkg.id

    def save_hooks(self, package_id: str, hooks_data: List[Any], selected_hook: Any) -> None:
        with get_db_session() as db:
            # We mock the single selected hook saving for now
            h = Hook(
                package_id=package_id,
                text=selected_hook.text,
                score=selected_hook.score,
                is_selected=True
            )
            db.add(h)

    def save_outline(self, package_id: str, outline_list: List[str]) -> None:
        with get_db_session() as db:
            o = Outline(
                package_id=package_id,
                structure_json={"outline": outline_list}
            )
            db.add(o)

    def create_script(self, package_id: str) -> str:
        with get_db_session() as db:
            s = Script(package_id=package_id)
            db.add(s)
            db.flush()
            return s.id

    def add_revision(self, script_id: str, iteration: int, text: str, feedback: Dict[str, Any]) -> None:
        with get_db_session() as db:
            rev = ScriptRevision(
                script_id=script_id,
                iteration=iteration,
                text=text,
                feedback_json=feedback
            )
            db.add(rev)
            
    def update_script_scores(self, script_id: str, fact: float, ret: float, qual: float) -> None:
        with get_db_session() as db:
            s = db.query(Script).filter(Script.id == script_id).first()
            if s:
                s.fact_score = fact
                s.retention_score = ret
                s.quality_score = qual

    def save_scenes(self, package_id: str, scenes: List[Any]) -> None:
        with get_db_session() as db:
            for s_data in scenes:
                s = Scene(
                    package_id=package_id,
                    scene_number=s_data.scene_number,
                    narration_text=s_data.narration_text,
                    visual_description=s_data.visual_description,
                    asset_type_required=s_data.asset_type_required
                )
                db.add(s)

    def complete_package(self, package_id: str, status: str = "FINALIZED") -> None:
        with get_db_session() as db:
            pkg = db.query(ContentPackage).filter(ContentPackage.id == package_id).first()
            if pkg:
                pkg.status = status
