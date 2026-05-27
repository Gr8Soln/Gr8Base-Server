from pwdlib import PasswordHash

_hash = PasswordHash.recommended()


def hash_password(plain: str) -> str:
    return _hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _hash.verify(plain, hashed)
