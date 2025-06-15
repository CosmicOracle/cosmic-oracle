# app/models/auth_models.py
"""
Pydantic Models for Authentication and User Management APIs.
"""
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, example="Jane Doe")
    email: EmailStr = Field(..., example="jane.doe@example.com")
    password: str = Field(..., min_length=8, example="a_strong_password123")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserProfile(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool