"""
Password reset utilities - Token generation and verification.
"""

import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from fastapi import HTTPException, status


def generate_reset_token(length: int = 32) -> str:
    """
    Generate a secure random token for password reset.
    
    Args:
        length: Token length (default 32 bytes)
        
    Returns:
        URL-safe random token
    """
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """
    Hash token using SHA256.
    Tokens are hashed before storing in DB for security.
    
    Args:
        token: Token to hash
        
    Returns:
        Hashed token
    """
    return hashlib.sha256(token.encode()).hexdigest()


def create_password_reset_token(
    db: Session,
    user_id: str,
    expires_in_hours: int = 24
) -> str:
    """
    Create and store a password reset token.
    
    Args:
        db: Database session
        user_id: User ID
        expires_in_hours: Token expiration time (default 24 hours)
        
    Returns:
        Plain token (to send via email)
        
    Raises:
        HTTPException: If user not found or DB error
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    # Generate token
    plain_token = generate_reset_token()
    hashed_token = hash_token(plain_token)
    
    # Create reset token record
    reset_token = PasswordResetToken(
        user_id=user_id,
        token=hashed_token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
    )
    
    db.add(reset_token)
    db.commit()
    
    return plain_token


def verify_reset_token(db: Session, plain_token: str) -> Optional[PasswordResetToken]:
    """
    Verify and retrieve a password reset token.
    
    Args:
        db: Database session
        plain_token: Plain token from user
        
    Returns:
        PasswordResetToken object if valid, None otherwise
    """
    hashed_token = hash_token(plain_token)
    
    # Find token
    token_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == hashed_token
    ).first()
    
    if not token_record:
        return None
    
    # Check if expired
    if token_record.is_expired():
        return None
    
    # Check if already used
    if token_record.is_used():
        return None
    
    return token_record


def invalidate_reset_tokens(db: Session, user_id: str) -> None:
    """
    Invalidate all password reset tokens for a user.
    Called after successful password reset.
    
    Args:
        db: Database session
        user_id: User ID
    """
    tokens = db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user_id,
        PasswordResetToken.used_at == None
    ).all()
    
    for token in tokens:
        token.mark_as_used()
    
    db.commit()
