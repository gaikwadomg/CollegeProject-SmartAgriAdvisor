"""
AgriSense AI - Database Manager
=================================

Provides centralized database connection management using SQLAlchemy.
Implements the session factory pattern with context managers for
safe transaction handling.

Usage:
    from database.database import DatabaseManager

    db = DatabaseManager()
    db.init_db()  # Create tables on first run

    with db.get_session() as session:
        users = session.query(User).all()

Author: AgriSense AI Team
"""

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import Settings
from database.models import Base
from utils.logger import get_logger

logger = get_logger(__name__)


# ── Enable SQLite Foreign Key Support ─────────────────────────────────
# SQLite does not enforce foreign keys by default.
# This event listener enables them for every connection.
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key enforcement for SQLite connections."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class DatabaseManager:
    """
    Centralized database connection and session management.

    Implements the singleton-like pattern where a single instance
    manages the engine and session factory for the entire application.

    Attributes:
        engine: SQLAlchemy engine instance
        SessionFactory: Session class bound to the engine
    """

    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize the database manager.

        Args:
            db_url: SQLAlchemy database URL. Uses default from Settings if None.
        """
        self._db_url = db_url or Settings.DB_URL
        self.engine = create_engine(
            self._db_url,
            echo=False,                    # Set True for SQL debug logging
            pool_pre_ping=True,            # Verify connections before use
            connect_args={"check_same_thread": False}  # SQLite threading
        )
        self.SessionFactory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
        logger.info(f"Database engine created: {self._db_url}")

    def init_db(self) -> None:
        """
        Create all database tables if they don't exist.
        Safe to call multiple times (uses CREATE IF NOT EXISTS).
        """
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def drop_all(self) -> None:
        """
        Drop all database tables. USE WITH CAUTION.
        Primarily for testing and development.
        """
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Provide a transactional session scope via context manager.

        Automatically commits on success and rolls back on error.
        The session is closed after the block exits.

        Usage:
            with db.get_session() as session:
                user = session.query(User).first()
                session.add(new_record)
                # Auto-commits here if no exception

        Yields:
            SQLAlchemy Session instance
        """
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction failed, rolled back: {e}")
            raise
        finally:
            session.close()

    def get_raw_session(self) -> Session:
        """
        Get a raw session without context management.
        Caller is responsible for commit/rollback/close.

        Returns:
            New Session instance
        """
        return self.SessionFactory()

    def health_check(self) -> bool:
        """
        Verify the database connection is working.

        Returns:
            True if the database is accessible
        """
        try:
            with self.get_session() as session:
                session.execute(
                    Base.metadata.tables["users"].select().limit(1)
                    if "users" in Base.metadata.tables
                    else "SELECT 1"
                )
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
