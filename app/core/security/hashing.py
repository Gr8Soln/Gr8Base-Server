import hashlib

def hash_string(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def compare_hash(value: str, hash_value: str) -> bool:
    return hash_string(value) == hash_value