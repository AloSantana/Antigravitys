"""
Tests for JWT authentication utilities in security.py.
"""

from datetime import timedelta

import pytest

from backend.security import create_access_token, decode_access_token
from fastapi import HTTPException


class TestCreateAccessToken:
    def test_returns_string(self):
        token = create_access_token("user123")
        assert isinstance(token, str)

    def test_subject_embedded(self):
        token = create_access_token("user123")
        payload = decode_access_token(token)
        assert payload["sub"] == "user123"

    def test_extra_claims_embedded(self):
        token = create_access_token("u1", extra_claims={"role": "admin"})
        payload = decode_access_token(token)
        assert payload["role"] == "admin"

    def test_expiry_set(self):
        token = create_access_token("u1")
        payload = decode_access_token(token)
        assert "exp" in payload

    def test_custom_expiry(self):
        token = create_access_token("u1", expires_delta=timedelta(hours=2))
        payload = decode_access_token(token)
        assert payload["exp"] > 0


class TestDecodeAccessToken:
    def test_round_trip(self):
        token = create_access_token("user42", extra_claims={"role": "user"})
        payload = decode_access_token(token)
        assert payload["sub"] == "user42"
        assert payload["role"] == "user"

    def test_expired_token_raises_401(self):
        token = create_access_token("u1", expires_delta=timedelta(seconds=-1))
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401

    def test_invalid_token_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("not.a.valid.token")
        assert exc_info.value.status_code == 401

    def test_tampered_token_raises_401(self):
        token = create_access_token("u1")
        # Flip a character near the end of the signature portion
        tampered = token[:-4] + "xxxx"
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(tampered)
        assert exc_info.value.status_code == 401
