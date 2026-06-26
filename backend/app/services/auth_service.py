"""
services/auth_service.py - Authentication Business Logic
=========================================================
This service handles:
1. Password hashing and verification (using bcrypt)
2. JWT token creation and validation

SECURITY CONCEPTS:
- Passwords: Never stored in plain text. We hash them with bcrypt.
  bcrypt is a slow hash algorithm — deliberately slow to resist brute force attacks.
  
- JWT (JSON Web Token): After login, we give the user a signed token.
  The token contains their user ID and role. Every subsequent API request
  includes this token in the Authorization header.
  
  Structure: header.payload.signature
  - header: algorithm used (HS256)
  - payload: {"sub": "user_id", "role": "admin", "exp": timestamp}
  - signature: cryptographic proof the token hasn't been tampered with

HOW JWT AUTH WORKS:
1. User sends username + password → we verify → return JWT token
2. User sends request with "Authorization: Bearer <token>" header
3. We validate the JWT signature and expiry → extract user_id
4. We load the user from DB using user_id → process request
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.database import get_collection


# ============================================================
# Password Hashing
# ============================================================

# CryptContext manages password hashing schemes
# bcrypt is the recommended modern password hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Converts a plain text password to a bcrypt hash.
    
    Example:
        hash_password("admin@123") 
        → "$2b$12$randomsalt...hashedvalue..."
    
    The hash is DIFFERENT every time (due to random salt) but
    verify_password() can still check if a plain password matches.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain password matches a stored hash.
    Returns True if they match, False otherwise.
    
    Example:
        verify_password("admin@123", stored_hash) → True
        verify_password("wrongpassword", stored_hash) → False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# JWT Token Management
# ============================================================

# OAuth2PasswordBearer tells FastAPI where to find the token in requests
# tokenUrl is the login endpoint (for Swagger UI integration)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a signed JWT token containing the provided data.
    
    Parameters:
        data: dict containing user info, e.g. {"sub": "user_id", "role": "admin"}
        expires_delta: how long until the token expires (default: from settings)
    
    Returns:
        JWT string like "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    """
    to_encode = data.copy()
    
    # Set expiry time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    
    # Sign and encode the token
    # settings.secret_key is the signing key — keep this SECRET!
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodes and validates a JWT token.
    
    Raises HTTPException if:
    - Token is invalid (tampered with)
    - Token has expired
    - Token is missing required fields
    
    Returns:
        The payload dict, e.g. {"sub": "user_id", "role": "admin"}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


# ============================================================
# Dependency Functions (used in route handlers)
# ============================================================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    FastAPI dependency that extracts and validates the current user from JWT.
    
    HOW DEPENDENCIES WORK IN FASTAPI:
    When you add `current_user: dict = Depends(get_current_user)` to a route,
    FastAPI automatically:
    1. Extracts the Bearer token from the Authorization header
    2. Calls this function to validate it
    3. Passes the result as the `current_user` parameter
    
    Usage in route:
        @router.get("/protected")
        async def protected_route(current_user = Depends(get_current_user)):
            return {"message": f"Hello {current_user['username']}"}
    """
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    
    # Load fresh user data from database
    users_col = get_collection("users")
    
    from bson import ObjectId
    try:
        user = await users_col.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid user ID in token")
    
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "role": user["role"]
    }


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency that ensures the current user is an admin.
    Use this for sensitive endpoints.
    
    Usage:
        @router.delete("/users/{id}")
        async def delete_user(current_user = Depends(require_admin)):
            ...
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
