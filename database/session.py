from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from .database import engine

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

@contextmanager
def get_db_session():
    """
    Provide a transactional scope around a series of operations.
    Usage:
        with get_db_session() as session:
            session.add(user)
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
