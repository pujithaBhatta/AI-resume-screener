"""
api/auth.py - Authentication Endpoints
========================================
Handles admin login and returns JWT tokens.
"""

from fastapi import APIRouter, HTTPException, status
from datetime import timedelta

from app.models.user import LoginRequest, TokenResponse
from app.services.auth_service import verify_password, create_access_token
from app.database import get_collection
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Admin login endpoint.
    
    1. Find user by username in MongoDB
    2. Verify password against stored bcrypt hash
    3. Return JWT access token
    """
    users_col = get_collection("users")
    
    # Find user by username
    user = await users_col.find_one({"username": request.username})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create JWT token
    token_data = {
        "sub": str(user["_id"]),
        "username": user["username"],
        "role": user["role"]
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        username=user["username"],
        role=user["role"]
    )


@router.get("/me")
async def get_me(current_user: dict = None):
    """Returns current logged-in user info."""
    from app.services.auth_service import get_current_user
    from fastapi import Depends
    return current_user
