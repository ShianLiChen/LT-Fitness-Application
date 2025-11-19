import bcrypt
from config import Config

def hash_password(password: str) -> str:
    """Hash password using bcrypt + pepper (no manual salt)."""
    pepper = Config.JWT_PEPPER or ""
    combined = (password + pepper).encode()
    hashed = bcrypt.hashpw(combined, bcrypt.gensalt())
    return hashed.decode()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password using bcrypt + pepper."""
    pepper = Config.JWT_PEPPER or ""
    combined = (password + pepper).encode()
    try:
        return bcrypt.checkpw(combined, stored_hash.encode())
    except ValueError:
        return False
