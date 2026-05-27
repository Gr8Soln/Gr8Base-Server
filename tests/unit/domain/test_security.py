from app.infrastructure.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_subject,
)
from app.infrastructure.security.password_handler import hash_password, verify_password


def test_password_hash_and_verify() -> None:
    plain = "supersecret123"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_hash_is_different_each_time() -> None:
    plain = "samepassword"
    h1 = hash_password(plain)
    h2 = hash_password(plain)
    # bcrypt salts mean same input → different hash
    assert h1 != h2
    # but both should verify
    assert verify_password(plain, h1)
    assert verify_password(plain, h2)


def test_create_and_decode_access_token() -> None:
    subject = "user-uuid-123"
    token = create_access_token(subject)

    payload = decode_token(token)
    assert payload["sub"] == subject
    assert payload["type"] == "access"


def test_create_and_decode_refresh_token() -> None:
    subject = "user-uuid-456"
    token = create_refresh_token(subject)

    payload = decode_token(token)
    assert payload["sub"] == subject
    assert payload["type"] == "refresh"


def test_get_subject_from_valid_token() -> None:
    subject = "user-uuid-789"
    token = create_access_token(subject)
    assert get_subject(token) == subject


def test_get_subject_from_invalid_token_returns_none() -> None:
    assert get_subject("not.a.valid.token") is None
    assert get_subject("") is None


def test_access_and_refresh_tokens_are_different() -> None:
    subject = "same-user"
    access = create_access_token(subject)
    refresh = create_refresh_token(subject)
    assert access != refresh
