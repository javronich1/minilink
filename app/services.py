import secrets
import string
from typing import Optional

ALPHABET = string.ascii_letters + string.digits

def gen_code(n: int = 7) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(n))

def sanitize_scheme(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")

def choose_code(custom: Optional[str]) -> str:
    return custom if custom else gen_code()