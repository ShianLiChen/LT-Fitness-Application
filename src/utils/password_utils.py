# src/utils/password_utils.py
import bcrypt
from config import Config


# -------------------------
# Password Utilities
# -------------------------
def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with a pepper.
    No manual salt is required as bcrypt generates it internally.
    """
    pepper = Config.JWT_PEPPER or ""
    combined = (password + pepper).encode()
    hashed = bcrypt.hashpw(combined, bcrypt.gensalt())
    return hashed.decode()


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against the stored bcrypt hash using the same pepper.
    Returns True if it matches, False otherwise.
    """
    pepper = Config.JWT_PEPPER or ""
    combined = (password + pepper).encode()
    try:
        return bcrypt.checkpw(combined, stored_hash.encode())
    except ValueError:
        return False
