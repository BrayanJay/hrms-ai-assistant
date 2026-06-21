from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings
from fastapi import HTTPException, status
from secrets import randbelow

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.secret_key

def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return password_context.verify(plain, hashed)

def create_access_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes),
        "type": "access"
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=settings.algorithm)

def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
        "type": "refresh"
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=settings.algorithm)

def decode_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[settings.algorithm])
        return decoded_token
    except JWTError: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
def generate_otp() -> str:
    return str(randbelow(1000000)).zfill(6)

def hash_otp(otp: str) -> str:
    return password_context.hash(otp)

def verify_otp(plain: str, hashed: str) -> bool:
    return password_context.verify(plain, hashed)