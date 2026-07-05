import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.session import get_db_session
from database.models import Topic

def inspect_db():
    print("Inspecting Database...")
    with get_db_session() as db:
        topics = db.query(Topic).all()
        for t in topics:
            print(f"Topic: {t.title} | Score: {t.score}")
            print(f" - Main Tech: {t.main_technology}")
            print("---")

if __name__ == "__main__":
    inspect_db()
