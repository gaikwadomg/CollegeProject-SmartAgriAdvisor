"""
AgriSense AI - Authentication Service
=======================================

Provides user authentication, registration, and password management.
Uses SHA-256 hashing for password storage (suitable for demo/academic
projects; production should use bcrypt or argon2).

Usage:
    from services.auth_service import AuthService
    from database.database import DatabaseManager

    db = DatabaseManager()
    auth = AuthService(db)
    
    success, user = auth.authenticate("admin", "admin123")

Author: AgriSense AI Team
"""

import hashlib
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func

from config.settings import Settings
from database.database import DatabaseManager
from database.models import User, LogEntry
from utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """
    Handles user authentication, registration, and account management.

    This service encapsulates all auth-related business logic,
    keeping it separate from the UI and database layers.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the auth service.

        Args:
            db_manager: DatabaseManager instance for session access
        """
        self._db = db_manager

    # ── Password Hashing ──────────────────────────────────────────────

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hash a password using SHA-256.

        Args:
            password: Plain-text password

        Returns:
            Hex-encoded hash string
        """
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain-text password to verify
            password_hash: Stored hash to compare against

        Returns:
            True if the password matches
        """
        return hashlib.sha256(password.encode("utf-8")).hexdigest() == password_hash

    # ── Authentication ────────────────────────────────────────────────

    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[User]]:
        """
        Authenticate a user with username and password.

        Args:
            username: The username to authenticate
            password: The plain-text password

        Returns:
            Tuple of (success: bool, user: User or None)
        """
        try:
            with self._db.get_session() as session:
                user = session.query(User).filter(
                    func.lower(User.username) == func.lower(username.strip()),
                    User.is_active == True
                ).first()

                if user is None:
                    logger.warning(f"Login failed: user '{username}' not found")
                    return False, None

                if not self._verify_password(password, user.password_hash):
                    logger.warning(f"Login failed: wrong password for '{username}'")
                    return False, None

                # Update last login timestamp
                user.last_login = datetime.utcnow()

                # Log the successful login
                log_entry = LogEntry(
                    user_id=user.id,
                    action="login",
                    details=f"User '{username}' logged in successfully"
                )
                session.add(log_entry)

                logger.info(f"User '{username}' authenticated successfully")

                # Expunge user from session so it can be used after session closes
                session.expunge(user)
                return True, user

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, None

    # ── Registration ──────────────────────────────────────────────────

    def register_user(
        self,
        username: str,
        password: str,
        full_name: str = "",
        email: str = "",
        role: str = "farmer"
    ) -> Tuple[bool, str]:
        """
        Register a new user account.

        Args:
            username: Unique username
            password: Plain-text password (will be hashed)
            full_name: User's full name
            email: Email address
            role: User role ('admin' or 'farmer')

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            with self._db.get_session() as session:
                # Check for existing username
                existing = session.query(User).filter_by(
                    username=username.strip()
                ).first()
                if existing:
                    return False, f"Username '{username}' already exists."

                new_user = User(
                    username=username.strip(),
                    password_hash=self._hash_password(password),
                    full_name=full_name.strip(),
                    email=email.strip() if email else None,
                    role=role,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                session.add(new_user)
                logger.info(f"New user registered: '{username}' (role: {role})")
                return True, "Registration successful!"

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, f"Registration failed: {str(e)}"

    # ── Password Management ───────────────────────────────────────────

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change a user's password.

        Args:
            user_id: ID of the user
            old_password: Current password for verification
            new_password: New password to set

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            with self._db.get_session() as session:
                user = session.query(User).filter_by(id=user_id).first()
                if not user:
                    return False, "User not found."

                if not self._verify_password(old_password, user.password_hash):
                    return False, "Current password is incorrect."

                user.password_hash = self._hash_password(new_password)

                log_entry = LogEntry(
                    user_id=user_id,
                    action="password_change",
                    details="Password changed successfully"
                )
                session.add(log_entry)

                logger.info(f"Password changed for user_id={user_id}")
                return True, "Password changed successfully!"

        except Exception as e:
            logger.error(f"Password change error: {e}")
            return False, f"Failed to change password: {str(e)}"

    # ── Default Admin Setup ───────────────────────────────────────────

    def ensure_default_admin(self) -> None:
        """
        Create the default admin user if no users exist.
        Called during application startup.
        """
        try:
            with self._db.get_session() as session:
                user_count = session.query(func.count(User.id)).scalar()
                if user_count == 0:
                    admin = User(
                        username=Settings.DEFAULT_ADMIN_USERNAME,
                        password_hash=self._hash_password(Settings.DEFAULT_ADMIN_PASSWORD),
                        full_name=Settings.DEFAULT_ADMIN_NAME,
                        email=Settings.DEFAULT_ADMIN_EMAIL,
                        role="admin",
                        is_active=True
                    )
                    session.add(admin)
                    logger.info("Default admin user created (admin/admin123)")

        except Exception as e:
            logger.error(f"Failed to create default admin: {e}")

    # ── User Queries ──────────────────────────────────────────────────

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by their ID."""
        try:
            with self._db.get_session() as session:
                user = session.query(User).filter_by(id=user_id).first()
                if user:
                    session.expunge(user)
                return user
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None

    def get_all_users(self) -> List[User]:
        """Get all active users."""
        try:
            with self._db.get_session() as session:
                users = session.query(User).filter_by(is_active=True).all()
                for u in users:
                    session.expunge(u)
                return users
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []
