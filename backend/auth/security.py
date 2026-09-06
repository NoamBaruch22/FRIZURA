from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from passlib.context import CryptContext
from backend.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str | Any, manager_id: int, role: str, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "manager_id": manager_id,
        "role": role,
        "iss": "frizura.auth"
    }
    
    # We load the private key directly from settings (it's stored as a string)
    private_key = settings.jwt_private_key.get_secret_value()
    encoded_jwt = jwt.encode(to_encode, private_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def decode_token(token: str) -> dict:
    public_key = settings.jwt_public_key
    try:
        decoded_token = jwt.decode(
            token, 
            public_key, 
            algorithms=[settings.jwt_algorithm],
            issuer="frizura.auth"
        )
        return decoded_token
    except jwt.PyJWTError:
        return None
