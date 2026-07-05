from sqlalchemy import create_engine
from config import config
from common import logger, DatabaseError
from .base import Base

def _create_engine():
    """Create the SQLAlchemy engine based on the connection string."""
    try:
        connect_args = {}
        # SQLite needs check_same_thread=False if used across threads
        if config.database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False

        db_engine = create_engine(
            config.database_url,
            connect_args=connect_args,
            # pool_pre_ping=True is recommended for production (Postgres)
            pool_pre_ping=not config.database_url.startswith("sqlite")
        )
        return db_engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise DatabaseError(f"Engine creation failed: {e}") from e

engine = _create_engine()

def init_db():
    """
    Create all tables in the database.
    In a real production environment, this should be handled by Alembic migrations.
    """
    try:
        logger.info(f"Initializing database at {config.database_url}")
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise DatabaseError(f"Database initialization failed: {e}") from e
