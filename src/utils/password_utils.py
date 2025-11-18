import bcrypt
from config import Config

def generate_salt() -> str:
    #Generate a random salt.
    return bcrypt.gensalt().decode()

def hash_password(password: str, salt: str) -> str:
    # Hash password using bcrypt + salt + pepper.
    pepper = Config.JWT_PEPPER
    combined = (password + salt + pepper).encode()

    return bcrypt.hashpw(combined, bcrypt.gensalt()).decode()

def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    # Verify a password using pepper+salt.
    pepper = Config.JWT_PEPPER
    combined = (password + salt + pepper).encode()

    return bcrypt.checkpw(combined, stored_hash.encode())
