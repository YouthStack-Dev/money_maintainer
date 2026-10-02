from datetime import datetime, timedelta, timezone
import hashlib, secrets, jwt
from pwdlib import PasswordHash
from app.core.config import settings

password_hash = PasswordHash.recommended()

def validate_password(password: str) -> None:
    if len(password) != 4 or not password.isdigit():
        raise ValueError("PIN must be exactly 4 digits")

def hash_password(password: str) -> str:
    validate_password(password)
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

def access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload={"sub":str(user_id),"role":role,"type":"access","iat":now,"exp":now+timedelta(minutes=settings.access_token_expire_minutes)}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

def refresh_token() -> str:
    return secrets.token_urlsafe(64)

def one_time_token() -> str:
    return secrets.token_urlsafe(48)

def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
