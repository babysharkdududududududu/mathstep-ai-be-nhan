"""
Email utilities for sending password reset and verification emails.

For production, integrate with SendGrid, AWS SES, or similar service.
This example uses simulated email sending (logs to console/file).
"""

import logging
from typing import Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_password_reset_email(
    email: str,
    reset_token: str,
    reset_url: Optional[str] = None
) -> bool:
    """
    Send password reset email to user.
    
    This is a simulated implementation. 
    For production, replace with actual email service (SendGrid, SES, etc.).
    
    Args:
        email: User email address
        reset_token: Plain reset token (to include in URL)
        reset_url: Optional custom reset URL (if not provided, constructs one)
        
    Returns:
        True if sent successfully, False otherwise
    """
    
    if not reset_url:
        # Construct reset URL - adjust to match your frontend URL
        reset_url = f"https://mathstep-ai-fe-7z28.vercel.app/reset-password?token={reset_token}"
    
    email_body = f"""
    <h2>Password Reset Request</h2>
    <p>Hello,</p>
    <p>You requested a password reset for your MathStep AI account.</p>
    <p>Click the link below to reset your password (expires in 24 hours):</p>
    <p>
        <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
            Reset Password
        </a>
    </p>
    <p>Or copy this link: {reset_url}</p>
    <p>If you did not request this, please ignore this email.</p>
    <p>Best,<br/>MathStep AI Team</p>
    """
    
    try:
        # TODO: Implement actual email sending here
        # Example services:
        # - SendGrid: from sendgrid import SendGridAPIClient
        # - AWS SES: import boto3
        # - SMTP: import smtplib
        
        # For now, log to console/file
        logger.info(f"[SIMULATED EMAIL] Password reset sent to {email}")
        logger.debug(f"Reset token: {reset_token}")
        logger.debug(f"Reset URL: {reset_url}")
        
        # In production, this should return actual send status
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return False


def send_email_verification(
    email: str,
    verification_url: Optional[str] = None
) -> bool:
    """
    Send email verification link to new user.
    
    Args:
        email: User email address
        verification_url: URL for email verification
        
    Returns:
        True if sent successfully, False otherwise
    """
    
    if not verification_url:
        verification_url = f"https://mathstep-ai-fe-7z28.vercel.app/verify-email"
    
    email_body = f"""
    <h2>Welcome to MathStep AI!</h2>
    <p>Thank you for signing up. Please verify your email address.</p>
    <p>
        <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
            Verify Email
        </a>
    </p>
    """
    
    try:
        logger.info(f"[SIMULATED EMAIL] Verification email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        return False
