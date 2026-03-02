"""
User Management Module

Manages user accounts using SQLite database.
Supports CRUD operations, search, role management, and statistics.
Passwords are stored as scrypt-hashed values (RFC 7914 / OWASP recommended).
"""

import hashlib
import json
import logging
import os
import secrets
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import uuid

logger = logging.getLogger(__name__)

VALID_ROLES = {"admin", "user", "viewer"}

# scrypt parameters (OWASP recommended minimums)
_SCRYPT_N = 2**14   # CPU/memory cost
_SCRYPT_R = 8       # block size
_SCRYPT_P = 1       # parallelism
_SCRYPT_DKLEN = 64  # derived key length (bytes)


def _hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Hash a password using scrypt (OWASP-recommended key derivation function).

    Args:
        password: Plain-text password to hash
        salt: Optional hex-encoded salt; a new one is generated if not provided

    Returns:
        Tuple of (hex-encoded hash, hex-encoded salt)
    """
    if not salt:
        salt = secrets.token_hex(32)
    hashed = hashlib.scrypt(
        password.encode(),
        salt=bytes.fromhex(salt),
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_SCRYPT_DKLEN,
    ).hex()
    return hashed, salt


class UserManager:
    """Manages user accounts with SQLite backend."""

    def __init__(self, db_path: str = "users.db") -> None:
        """
        Initialize the user manager.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_database()
        logger.info(f"UserManager initialized with database: {db_path}")

    def _init_database(self) -> None:
        """Initialize the database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        full_name TEXT,
                        role TEXT NOT NULL DEFAULT 'user',
                        is_active INTEGER NOT NULL DEFAULT 1,
                        hashed_password TEXT NOT NULL,
                        password_salt TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_users_username
                    ON users(username)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_users_email
                    ON users(email)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_users_role
                    ON users(role)
                """)

                conn.commit()
                logger.info("UserManager database schema initialized successfully")

        except sqlite3.Error as e:
            logger.error(f"Failed to initialize UserManager database: {e}", exc_info=True)
            raise

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new user.

        Args:
            username: Unique username
            email: Unique email address
            password: Plain-text password (will be hashed)
            full_name: Optional display name
            role: User role — must be one of admin / user / viewer
            metadata: Optional extra metadata

        Returns:
            Created user data (without password fields)

        Raises:
            ValueError: If role is invalid
            sqlite3.IntegrityError: If username or email already exists
        """
        if role not in VALID_ROLES:
            raise ValueError(f"Invalid role '{role}'. Must be one of: {', '.join(sorted(VALID_ROLES))}")

        user_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        hashed_pw, salt = _hash_password(password)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO users
                        (id, username, email, full_name, role, is_active,
                         hashed_password, password_salt, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        username,
                        email,
                        full_name,
                        role,
                        hashed_pw,
                        salt,
                        timestamp,
                        timestamp,
                        json.dumps(metadata or {}),
                    ),
                )
                conn.commit()

            logger.info(f"Created user: {user_id} ({username})")
            return {
                "id": user_id,
                "username": username,
                "email": email,
                "full_name": full_name,
                "role": role,
                "is_active": True,
                "created_at": timestamp,
                "updated_at": timestamp,
                "metadata": metadata or {},
            }

        except sqlite3.IntegrityError as e:
            logger.warning(f"User creation failed — duplicate username/email: {e}")
            raise
        except sqlite3.Error as e:
            logger.error(f"Failed to create user: {e}", exc_info=True)
            raise

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user by ID.

        Args:
            user_id: User UUID

        Returns:
            User data dict or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, email, full_name, role, is_active, "
                    "created_at, updated_at, metadata FROM users WHERE id = ?",
                    (user_id,),
                )
                row = cursor.fetchone()

                if not row:
                    return None

                user = dict(row)
                user["is_active"] = bool(user["is_active"])
                user["metadata"] = json.loads(user["metadata"] or "{}")
                return user

        except sqlite3.Error as e:
            logger.error(f"Failed to get user {user_id}: {e}", exc_info=True)
            raise

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a user by username.

        Args:
            username: Username string

        Returns:
            User data dict or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, email, full_name, role, is_active, "
                    "created_at, updated_at, metadata FROM users WHERE username = ?",
                    (username,),
                )
                row = cursor.fetchone()

                if not row:
                    return None

                user = dict(row)
                user["is_active"] = bool(user["is_active"])
                user["metadata"] = json.loads(user["metadata"] or "{}")
                return user

        except sqlite3.Error as e:
            logger.error(f"Failed to get user by username '{username}': {e}", exc_info=True)
            raise

    def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        List users with optional filtering and pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            role: Filter by role
            is_active: Filter by active status

        Returns:
            Tuple of (users list, total count)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Build WHERE clause from known column names only (no user input injected)
                conditions: List[str] = []
                params: List[Any] = []
                if role is not None:
                    conditions.append("role = ?")
                    params.append(role)
                if is_active is not None:
                    conditions.append("is_active = ?")
                    params.append(1 if is_active else 0)

                if conditions:
                    where_sql = "WHERE " + " AND ".join(conditions)
                    count_sql = f"SELECT COUNT(*) as count FROM users {where_sql}"
                    list_sql = (
                        "SELECT id, username, email, full_name, role, is_active, "
                        "created_at, updated_at, metadata "
                        f"FROM users {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?"
                    )
                else:
                    count_sql = "SELECT COUNT(*) as count FROM users"
                    list_sql = (
                        "SELECT id, username, email, full_name, role, is_active, "
                        "created_at, updated_at, metadata "
                        "FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?"
                    )

                cursor.execute(count_sql, params)
                total = cursor.fetchone()["count"]

                cursor.execute(list_sql, params + [limit, skip])

                users = []
                for row in cursor.fetchall():
                    user = dict(row)
                    user["is_active"] = bool(user["is_active"])
                    user["metadata"] = json.loads(user["metadata"] or "{}")
                    users.append(user)

                return users, total

        except sqlite3.Error as e:
            logger.error(f"Failed to list users: {e}", exc_info=True)
            raise

    def update_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing user's fields.

        Args:
            user_id: User UUID
            email: New email address (optional)
            full_name: New display name (optional)
            role: New role (optional)
            is_active: New active status (optional)
            metadata: New metadata (optional, replaces existing)

        Returns:
            Updated user data or None if not found

        Raises:
            ValueError: If role is invalid
        """
        if role is not None and role not in VALID_ROLES:
            raise ValueError(f"Invalid role '{role}'. Must be one of: {', '.join(sorted(VALID_ROLES))}")

        # Map of allowed column names → values (hardcoded keys prevent injection)
        column_values: Dict[str, Any] = {}
        if email is not None:
            column_values["email"] = email
        if full_name is not None:
            column_values["full_name"] = full_name
        if role is not None:
            column_values["role"] = role
        if is_active is not None:
            column_values["is_active"] = 1 if is_active else 0
        if metadata is not None:
            column_values["metadata"] = json.dumps(metadata)

        if not column_values:
            return self.get_user(user_id)

        timestamp = datetime.utcnow().isoformat()
        column_values["updated_at"] = timestamp

        # Build SET clause from known column names only (values remain parameterized)
        set_clause = ", ".join(f"{col} = ?" for col in column_values)
        params: List[Any] = list(column_values.values()) + [user_id]

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE users SET {set_clause} WHERE id = ?",
                    params,
                )
                conn.commit()

                if cursor.rowcount == 0:
                    return None

            logger.info(f"Updated user: {user_id}")
            return self.get_user(user_id)

        except sqlite3.Error as e:
            logger.error(f"Failed to update user {user_id}: {e}", exc_info=True)
            raise

    def update_password(self, user_id: str, new_password: str) -> bool:
        """
        Update a user's password.

        Args:
            user_id: User UUID
            new_password: New plain-text password (will be hashed)

        Returns:
            True if updated, False if user not found
        """
        hashed_pw, salt = _hash_password(new_password)
        timestamp = datetime.utcnow().isoformat()

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE users
                    SET hashed_password = ?, password_salt = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (hashed_pw, salt, timestamp, user_id),
                )
                conn.commit()
                updated = cursor.rowcount > 0

            if updated:
                logger.info(f"Password updated for user: {user_id}")
            return updated

        except sqlite3.Error as e:
            logger.error(f"Failed to update password for user {user_id}: {e}", exc_info=True)
            raise

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.

        Args:
            user_id: User UUID

        Returns:
            True if deleted, False if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                deleted = cursor.rowcount > 0

            if deleted:
                logger.info(f"Deleted user: {user_id}")
            else:
                logger.warning(f"User not found for deletion: {user_id}")
            return deleted

        except sqlite3.Error as e:
            logger.error(f"Failed to delete user {user_id}: {e}", exc_info=True)
            raise

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def verify_password(self, user_id: str, password: str) -> bool:
        """
        Verify a user's password.

        Args:
            user_id: User UUID
            password: Plain-text password to verify

        Returns:
            True if the password is correct, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT hashed_password, password_salt FROM users WHERE id = ?",
                    (user_id,),
                )
                row = cursor.fetchone()

                if not row:
                    return False

                expected, _ = _hash_password(password, salt=row["password_salt"])
                return secrets.compare_digest(expected, row["hashed_password"])

        except sqlite3.Error as e:
            logger.error(f"Failed to verify password for user {user_id}: {e}", exc_info=True)
            raise

    # ------------------------------------------------------------------
    # Search & statistics
    # ------------------------------------------------------------------

    def search_users(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search users by username, email, or full name.

        Args:
            query: Search string
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            Tuple of (matching users list, total count)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                pattern = f"%{query}%"

                cursor.execute(
                    """
                    SELECT COUNT(*) as count FROM users
                    WHERE username LIKE ? OR email LIKE ? OR full_name LIKE ?
                    """,
                    (pattern, pattern, pattern),
                )
                total = cursor.fetchone()["count"]

                cursor.execute(
                    """
                    SELECT id, username, email, full_name, role, is_active,
                           created_at, updated_at, metadata
                    FROM users
                    WHERE username LIKE ? OR email LIKE ? OR full_name LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (pattern, pattern, pattern, limit, skip),
                )

                users = []
                for row in cursor.fetchall():
                    user = dict(row)
                    user["is_active"] = bool(user["is_active"])
                    user["metadata"] = json.loads(user["metadata"] or "{}")
                    users.append(user)

                logger.info(f"Found {len(users)} users matching '{query}'")
                return users, total

        except sqlite3.Error as e:
            logger.error(f"Failed to search users: {e}", exc_info=True)
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        Return aggregate statistics about the user base.

        Returns:
            Dictionary containing user statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) as count FROM users")
                total_users = cursor.fetchone()["count"]

                cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = 1")
                active_users = cursor.fetchone()["count"]

                cursor.execute("""
                    SELECT role, COUNT(*) as count
                    FROM users
                    GROUP BY role
                """)
                by_role = {row["role"]: row["count"] for row in cursor.fetchall()}

                cursor.execute("""
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM users
                    WHERE created_at >= date('now', '-7 days')
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                """)
                recent_registrations = [dict(row) for row in cursor.fetchall()]

                return {
                    "total_users": total_users,
                    "active_users": active_users,
                    "inactive_users": total_users - active_users,
                    "by_role": by_role,
                    "recent_registrations": recent_registrations,
                }

        except sqlite3.Error as e:
            logger.error(f"Failed to get user statistics: {e}", exc_info=True)
            raise

    def close(self) -> None:
        """Close the manager. (SQLite auto-closes connections; kept for consistency.)"""
        logger.info("UserManager closed")
