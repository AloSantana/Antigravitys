"""
Tests for UserManager

Comprehensive test suite for user management persistence.
"""

import os
import sqlite3
import tempfile

import pytest

from backend.user_manager import UserManager, _hash_password, VALID_ROLES


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_db():
    """Create a temporary SQLite database file for testing."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmp.close()
    yield tmp.name
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)


@pytest.fixture
def manager(temp_db):
    """Return a fresh UserManager backed by a temporary database."""
    return UserManager(db_path=temp_db)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_user(manager: UserManager, username: str = "alice", **kwargs) -> dict:
    defaults = {
        "email": f"{username}@example.com",
        "password": "S3cureP@ss!",
        "full_name": username.capitalize(),
        "role": "user",
    }
    defaults.update(kwargs)
    return manager.create_user(username=username, **defaults)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

class TestHashPassword:
    def test_produces_hex_string(self):
        hashed, salt = _hash_password("my_password")
        assert isinstance(hashed, str)
        assert len(hashed) == 128  # scrypt dklen=64 bytes → 128 hex chars

    def test_same_password_and_salt_produces_same_hash(self):
        hashed1, salt = _hash_password("abc123")
        hashed2, _ = _hash_password("abc123", salt=salt)
        assert hashed1 == hashed2

    def test_different_passwords_produce_different_hashes(self):
        h1, salt = _hash_password("password1")
        h2, _ = _hash_password("password2", salt=salt)
        assert h1 != h2

    def test_auto_generates_salt(self):
        _, salt1 = _hash_password("pw")
        _, salt2 = _hash_password("pw")
        assert salt1 != salt2


# ---------------------------------------------------------------------------
# Database initialisation
# ---------------------------------------------------------------------------

class TestInitDatabase:
    def test_creates_users_table(self, temp_db):
        UserManager(db_path=temp_db)
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            )
            assert cursor.fetchone() is not None

    def test_creates_indexes(self, temp_db):
        UserManager(db_path=temp_db)
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='users'"
            )
            index_names = {row[0] for row in cursor.fetchall()}
        assert "idx_users_username" in index_names
        assert "idx_users_email" in index_names

    def test_idempotent_on_second_init(self, temp_db):
        """Creating a second UserManager on the same DB should not raise."""
        UserManager(db_path=temp_db)
        UserManager(db_path=temp_db)  # should not raise


# ---------------------------------------------------------------------------
# create_user
# ---------------------------------------------------------------------------

class TestCreateUser:
    def test_returns_expected_fields(self, manager):
        user = _make_user(manager)
        assert "id" in user
        assert user["username"] == "alice"
        assert user["email"] == "alice@example.com"
        assert user["full_name"] == "Alice"
        assert user["role"] == "user"
        assert user["is_active"] is True
        assert "created_at" in user
        assert "updated_at" in user
        assert "metadata" in user
        # Password must NOT be returned
        assert "hashed_password" not in user
        assert "password_salt" not in user

    def test_default_role_is_user(self, manager):
        user = manager.create_user(
            username="bob", email="bob@example.com", password="P@ssw0rd!"
        )
        assert user["role"] == "user"

    def test_admin_role_accepted(self, manager):
        user = manager.create_user(
            username="admin_user",
            email="admin@example.com",
            password="P@ssw0rd!",
            role="admin",
        )
        assert user["role"] == "admin"

    def test_viewer_role_accepted(self, manager):
        user = manager.create_user(
            username="viewer_user",
            email="viewer@example.com",
            password="P@ssw0rd!",
            role="viewer",
        )
        assert user["role"] == "viewer"

    def test_invalid_role_raises_value_error(self, manager):
        with pytest.raises(ValueError, match="Invalid role"):
            manager.create_user(
                username="bad_role",
                email="bad@example.com",
                password="P@ssw0rd!",
                role="superuser",
            )

    def test_duplicate_username_raises_integrity_error(self, manager):
        _make_user(manager)
        with pytest.raises(sqlite3.IntegrityError):
            manager.create_user(
                username="alice",
                email="different@example.com",
                password="P@ssw0rd!",
            )

    def test_duplicate_email_raises_integrity_error(self, manager):
        _make_user(manager)
        with pytest.raises(sqlite3.IntegrityError):
            manager.create_user(
                username="different_user",
                email="alice@example.com",
                password="P@ssw0rd!",
            )

    def test_metadata_is_stored(self, manager):
        user = manager.create_user(
            username="meta_user",
            email="meta@example.com",
            password="P@ssw0rd!",
            metadata={"team": "engineering"},
        )
        assert user["metadata"] == {"team": "engineering"}

    def test_metadata_defaults_to_empty_dict(self, manager):
        user = _make_user(manager)
        assert user["metadata"] == {}


# ---------------------------------------------------------------------------
# get_user / get_user_by_username
# ---------------------------------------------------------------------------

class TestGetUser:
    def test_get_user_returns_correct_data(self, manager):
        created = _make_user(manager)
        fetched = manager.get_user(created["id"])
        assert fetched is not None
        assert fetched["id"] == created["id"]
        assert fetched["username"] == "alice"

    def test_get_user_returns_none_for_missing_id(self, manager):
        assert manager.get_user("nonexistent-id") is None

    def test_get_user_by_username(self, manager):
        _make_user(manager)
        user = manager.get_user_by_username("alice")
        assert user is not None
        assert user["username"] == "alice"

    def test_get_user_by_username_returns_none_when_not_found(self, manager):
        assert manager.get_user_by_username("ghost") is None


# ---------------------------------------------------------------------------
# list_users
# ---------------------------------------------------------------------------

class TestListUsers:
    def test_lists_all_users(self, manager):
        _make_user(manager, "user1", email="u1@ex.com")
        _make_user(manager, "user2", email="u2@ex.com")
        users, total = manager.list_users()
        assert total == 2
        assert len(users) == 2

    def test_empty_database_returns_zero(self, manager):
        users, total = manager.list_users()
        assert total == 0
        assert users == []

    def test_pagination_skip(self, manager):
        for i in range(5):
            _make_user(manager, f"user{i}", email=f"u{i}@ex.com")
        users, total = manager.list_users(skip=3, limit=10)
        assert total == 5
        assert len(users) == 2

    def test_pagination_limit(self, manager):
        for i in range(5):
            _make_user(manager, f"user{i}", email=f"u{i}@ex.com")
        users, total = manager.list_users(skip=0, limit=3)
        assert total == 5
        assert len(users) == 3

    def test_filter_by_role(self, manager):
        _make_user(manager, "admin_u", email="a@ex.com", role="admin")
        _make_user(manager, "viewer_u", email="v@ex.com", role="viewer")
        _make_user(manager, "user_u", email="u@ex.com", role="user")

        admins, total = manager.list_users(role="admin")
        assert total == 1
        assert admins[0]["role"] == "admin"

    def test_filter_by_is_active(self, manager):
        created = _make_user(manager)
        manager.update_user(created["id"], is_active=False)

        active, _ = manager.list_users(is_active=True)
        inactive, _ = manager.list_users(is_active=False)
        assert all(u["is_active"] for u in active)
        assert all(not u["is_active"] for u in inactive)


# ---------------------------------------------------------------------------
# update_user
# ---------------------------------------------------------------------------

class TestUpdateUser:
    def test_update_full_name(self, manager):
        user = _make_user(manager)
        updated = manager.update_user(user["id"], full_name="Alice Smith")
        assert updated["full_name"] == "Alice Smith"

    def test_update_email(self, manager):
        user = _make_user(manager)
        updated = manager.update_user(user["id"], email="newalice@example.com")
        assert updated["email"] == "newalice@example.com"

    def test_update_role(self, manager):
        user = _make_user(manager)
        updated = manager.update_user(user["id"], role="admin")
        assert updated["role"] == "admin"

    def test_update_is_active(self, manager):
        user = _make_user(manager)
        updated = manager.update_user(user["id"], is_active=False)
        assert updated["is_active"] is False

    def test_update_invalid_role_raises_value_error(self, manager):
        user = _make_user(manager)
        with pytest.raises(ValueError, match="Invalid role"):
            manager.update_user(user["id"], role="god")

    def test_update_returns_none_for_missing_user(self, manager):
        result = manager.update_user("nonexistent-id", full_name="Ghost")
        assert result is None

    def test_no_op_update_returns_user(self, manager):
        user = _make_user(manager)
        result = manager.update_user(user["id"])
        assert result is not None
        assert result["id"] == user["id"]

    def test_updated_at_changes(self, manager):
        import time
        user = _make_user(manager)
        original_updated_at = user["updated_at"]
        time.sleep(0.01)
        updated = manager.update_user(user["id"], full_name="New Name")
        assert updated["updated_at"] >= original_updated_at


# ---------------------------------------------------------------------------
# update_password
# ---------------------------------------------------------------------------

class TestUpdatePassword:
    def test_update_password_returns_true(self, manager):
        user = _make_user(manager)
        assert manager.update_password(user["id"], "N3wSecureP@ss!") is True

    def test_update_password_returns_false_for_missing_user(self, manager):
        assert manager.update_password("nonexistent-id", "NewP@ss!") is False

    def test_old_password_no_longer_valid_after_update(self, manager):
        user = _make_user(manager, password="OldP@ss!")
        manager.update_password(user["id"], "N3wP@ss!")
        assert not manager.verify_password(user["id"], "OldP@ss!")

    def test_new_password_valid_after_update(self, manager):
        user = _make_user(manager, password="OldP@ss!")
        manager.update_password(user["id"], "N3wP@ss!")
        assert manager.verify_password(user["id"], "N3wP@ss!")


# ---------------------------------------------------------------------------
# verify_password
# ---------------------------------------------------------------------------

class TestVerifyPassword:
    def test_correct_password_returns_true(self, manager):
        user = _make_user(manager, password="CorrectP@ss!")
        assert manager.verify_password(user["id"], "CorrectP@ss!") is True

    def test_wrong_password_returns_false(self, manager):
        user = _make_user(manager, password="CorrectP@ss!")
        assert manager.verify_password(user["id"], "WrongP@ss!") is False

    def test_verify_returns_false_for_missing_user(self, manager):
        assert manager.verify_password("nonexistent-id", "anypassword") is False


# ---------------------------------------------------------------------------
# delete_user
# ---------------------------------------------------------------------------

class TestDeleteUser:
    def test_delete_existing_user_returns_true(self, manager):
        user = _make_user(manager)
        assert manager.delete_user(user["id"]) is True

    def test_deleted_user_no_longer_retrievable(self, manager):
        user = _make_user(manager)
        manager.delete_user(user["id"])
        assert manager.get_user(user["id"]) is None

    def test_delete_nonexistent_user_returns_false(self, manager):
        assert manager.delete_user("nonexistent-id") is False


# ---------------------------------------------------------------------------
# search_users
# ---------------------------------------------------------------------------

class TestSearchUsers:
    def test_search_by_username_prefix(self, manager):
        _make_user(manager, "alice_jones", email="aj@ex.com")
        _make_user(manager, "bob_smith", email="bs@ex.com")
        users, total = manager.search_users("alice")
        assert total == 1
        assert users[0]["username"] == "alice_jones"

    def test_search_by_email(self, manager):
        _make_user(manager, "user_x", email="unique_email@company.org")
        users, total = manager.search_users("company.org")
        assert total == 1

    def test_search_by_full_name(self, manager):
        _make_user(manager, "charlie", email="c@ex.com", full_name="Charles Darwin")
        users, total = manager.search_users("Darwin")
        assert total == 1

    def test_search_returns_empty_for_no_match(self, manager):
        _make_user(manager)
        users, total = manager.search_users("zzznomatch")
        assert total == 0
        assert users == []

    def test_search_pagination(self, manager):
        for i in range(5):
            _make_user(manager, f"testuser{i}", email=f"t{i}@ex.com")
        users, total = manager.search_users("testuser", skip=2, limit=2)
        assert total == 5
        assert len(users) == 2


# ---------------------------------------------------------------------------
# get_statistics
# ---------------------------------------------------------------------------

class TestGetStatistics:
    def test_empty_db_statistics(self, manager):
        stats = manager.get_statistics()
        assert stats["total_users"] == 0
        assert stats["active_users"] == 0
        assert stats["inactive_users"] == 0
        assert stats["by_role"] == {}
        assert stats["recent_registrations"] == []

    def test_statistics_counts(self, manager):
        _make_user(manager, "u1", email="u1@ex.com", role="admin")
        _make_user(manager, "u2", email="u2@ex.com", role="user")
        u3 = _make_user(manager, "u3", email="u3@ex.com", role="viewer")
        manager.update_user(u3["id"], is_active=False)

        stats = manager.get_statistics()
        assert stats["total_users"] == 3
        assert stats["active_users"] == 2
        assert stats["inactive_users"] == 1
        assert stats["by_role"]["admin"] == 1
        assert stats["by_role"]["user"] == 1
        assert stats["by_role"]["viewer"] == 1

    def test_recent_registrations_included(self, manager):
        _make_user(manager)
        stats = manager.get_statistics()
        assert len(stats["recent_registrations"]) >= 1


# ---------------------------------------------------------------------------
# VALID_ROLES constant
# ---------------------------------------------------------------------------

class TestValidRoles:
    def test_valid_roles_set(self):
        assert VALID_ROLES == {"admin", "user", "viewer"}
