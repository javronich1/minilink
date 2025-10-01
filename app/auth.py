# app/auth.py
from passlib.context import CryptContext

# Use PBKDF2-SHA256 to avoid bcrypt’s 72-byte password limit & backend quirks.
_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(plain: str) -> str:
    return _pwd.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)