"""
Authentication utilities for JWT tokens and password hashing
"""

import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from flask import current_app
import os
import bcrypt

# Patch bcrypt metadata for Passlib compatibility (bcrypt>=4.0 removed __about__)
if not hasattr(bcrypt, "__about__"):
    class _BcryptAbout:
        __version__ = getattr(bcrypt, "__version__", "unknown")
    bcrypt.__about__ = _BcryptAbout()  # type: ignore[attr-defined]

# Password hashing context
# bcrypt_sha256 removes the 72-byte input limit while keeping bcrypt's strength
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

# JWT configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.JWTError:
        raise ValueError("Invalid token")

def get_user_id_from_token(token: str) -> int:
    """Extract user ID from JWT token"""
    payload = verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise ValueError("Token does not contain user ID")
    return int(user_id)
