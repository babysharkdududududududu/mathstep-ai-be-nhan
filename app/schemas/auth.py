"""
Pydantic schemas for authentication.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime


class RegisterRequest(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Literal["STUDENT", "PARENT"] = "STUDENT"
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    name: Optional[str] = None
    
    def get_full_name(self) -> str:
        """Extract full name from firstName/lastName or name field."""
        if self.firstName or self.lastName:
            return f"{self.firstName or ''} {self.lastName or ''} ".strip()
        return self.name or "User"


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    """Schema for Google OAuth login."""
    token: str  # Google ID token


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user_id: UUID
    email: str
    role: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudentResponse(BaseModel):
    """Schema for student response."""
    id: UUID
    user_id: UUID
    name: Optional[str] = None
    grade_level: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ParentResponse(BaseModel):
    """Schema for parent response."""
    id: UUID
    user_id: UUID
    name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schema for password reset."""
    token: str
    new_password: str = Field(..., min_length=8)


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str
