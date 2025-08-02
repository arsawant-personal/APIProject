from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.logging import logger, log_authentication, log_token_operation

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.debug("🔐 Verifying password")
    result = pwd_context.verify(plain_password, hashed_password)
    logger.debug(f"🔐 Password verification result: {result}")
    return result

def get_password_hash(password: str) -> str:
    logger.debug("🔐 Hashing password")
    hashed = pwd_context.hash(password)
    logger.debug("🔐 Password hashed successfully")
    return hashed

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    logger.debug(f"🔑 Creating access token for user: {data.get('sub', 'unknown')}")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    log_token_operation("CREATE", data.get('sub', 'unknown'), "ACCESS")
    return encoded_jwt

def create_refresh_token(data: dict):
    logger.debug(f"🔑 Creating refresh token for user: {data.get('sub', 'unknown')}")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    log_token_operation("CREATE", data.get('sub', 'unknown'), "REFRESH")
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    logger.debug("🔑 Verifying token")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug(f"🔑 Token verified successfully for user: {payload.get('sub', 'unknown')}")
        return payload
    except JWTError as e:
        logger.warning(f"🔑 Token verification failed: {e}")
        return None 