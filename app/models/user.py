"""
User model.
"""

from sqlalchemy import Column, String, Enum, DateTime, func, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from enum import Enum as PyEnum
from datetime import datetime
from app.db.base import Base


class UserRole(str, PyEnum):
    """Enum for user roles."""
    STUDENT = "STUDENT"
    PARENT = "PARENT"


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)  # Nullable for OAuth users
    google_id = Column(String, unique=True, nullable=True, index=True)
    auth_provider = Column(String, default="local", nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    display_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    preferred_language = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", uselist=False, back_populates="user")
    parent = relationship("Parent", uselist=False, back_populates="user")
    
    def __repr__(self):
        return (
            f"<User(id={self.id}, email={self.email}, role={self.role}, "
            f"display_name={self.display_name})>"
        )
        
# app/models/user.py - thêm class UserProfile vào

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id                 = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id            = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                                nullable=False, unique=True, index=True)
    display_name       = Column(String(80),  nullable=True)
    avatar_url         = Column(Text,        nullable=True)
    avatar_frame_style = Column(String(40),  nullable=True, default="default")
    title              = Column(String(80),  nullable=True)
    created_at         = Column(DateTime(timezone=True), server_default=func.now())
    updated_at         = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="profile")
