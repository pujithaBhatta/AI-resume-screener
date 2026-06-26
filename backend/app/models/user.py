"""
models/user.py - User Data Models
===================================
Pydantic models define the SHAPE of our data.
Think of them as typed blueprints for what data looks like.

HOW PYDANTIC WORKS:
- You define a class with typed fields
- Pydantic validates data automatically (e.g., email must be valid email format)
- FastAPI uses these models to validate request bodies and generate API docs
- If data is invalid, FastAPI returns a clear 422 error automatically

DIFFERENT MODEL TYPES (pattern used throughout this project):
- Base model:    Common fields shared by all variants
- Create model:  Fields needed to CREATE a new record (no _id yet)
- Response model: Fields returned to the client (may exclude sensitive data like password)
- DB model:      Full record as stored in MongoDB
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ============================================================
# Request Models (what clients send TO the API)
# ============================================================

class LoginRequest(BaseModel):
    """
    Data sent when an admin logs in.
    
    Example request body:
        { "username": "admin", "password": "admin@123" }
    """
    username: str = Field(..., min_length=3, max_length=50, description="Admin username")
    password: str = Field(..., min_length=6, description="Admin password")


class CreateUserRequest(BaseModel):
    """Data needed to create a new admin user."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr                  # pydantic validates email format automatically
    password: str = Field(..., min_length=6)
    role: str = Field(default="admin", pattern="^(admin|viewer)$")  # Must be admin or viewer


# ============================================================
# Response Models (what the API sends BACK to clients)
# ============================================================

class TokenResponse(BaseModel):
    """
    Returned after successful login.
    
    access_token: JWT string (client stores this and sends with every request)
    token_type: Always "bearer" (industry standard)
    """
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class UserResponse(BaseModel):
    """User data returned to the client (NO password included)."""
    id: str
    username: str
    email: str
    role: str
    created_at: datetime
    
    class Config:
        # Allow using MongoDB's _id field mapped to 'id'
        populate_by_name = True
