"""
Password reset token model.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone, timedelta
from app.db.base import Base


class PasswordResetToken(Base):
    """Model for password reset tokens with expiration."""
    __tablename__ = "password_reset_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)  # Hashed token
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)  # Track if token was used
    
    # Relationship
    user = relationship("User")
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    def is_used(self) -> bool:
        """Check if token has been used."""
        return self.used_at is not None
    
    def mark_as_used(self):
        """Mark token as used."""
        self.used_at = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, expired={self.is_expired()})>"
