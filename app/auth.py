from passlib.context import CryptContext

# Use PBKDF2-SHA256 as bcrypt has 72-byte limit password (gave me headaches)
_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# hashes plaintext password; args a plaintext string and returns a hashed password (secure)
def hash_password(plain: str) -> str:
    return _pwd.hash(plain)

# verifies a plaintext password against a hashed password; args are plaintext and hashed, returns bool
def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)