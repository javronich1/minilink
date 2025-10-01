# helper functions for random short code generation, url scheme validation, selection between custom and generated codes

import secrets
import string
from typing import Optional

# defines character set used for generating random short codes (A-Z, a-z, 0-9)
ALPHABET = string.ascii_letters + string.digits

# -----------------------------------------------------
# Functions
# -----------------------------------------------------

# generates a random short code of length n (default 7) using the defined ALPHABET
def gen_code(n: int = 7) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(n))

# checks if the given URL starts with http:// or https://, returns True if valid, else False
def sanitize_scheme(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")

# chooses between a custom short code provided by the user and a generated one; returns the custom if given, else generates a new code
def choose_code(custom: Optional[str]) -> str:
    return custom if custom else gen_code()