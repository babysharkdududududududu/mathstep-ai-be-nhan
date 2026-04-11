"""
Email utilities for sending password reset emails via SMTP (Gmail).
Uses Gmail SMTP with TLS encryption.
"""

import smtplib
import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_password_reset_email(
    email: str,
    reset_token: str,
    reset_url: Optional[str] = None
) -> bool:
    """
    Send password reset email to user via SMTP (Gmail).
    
    Args:
        email: User email address
        reset_token: Plain reset token (to include in URL)
        reset_url: Optional custom reset URL (if not provided, constructs one)
        
    Returns:
        True if sent successfully, False otherwise
    """
    
    # Validate SMTP configuration
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD or not settings.SMTP_FROM:
        logger.error("SMTP configuration incomplete. Check .env variables: SMTP_USER, SMTP_PASSWORD, SMTP_FROM")
        return False
    
    if not reset_url:
        # Construct reset URL - adjust to match your frontend URL
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
    
    # Construct email body
    email_subject = "Password Reset Request - MathStep AI"
    
    email_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 4px; }}
            .content {{ padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 4px; margin-top: 20px; }}
            .button {{ display: inline-block; background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
            .footer {{ font-size: 12px; color: #999; margin-top: 20px; text-align: center; }}
            .warning {{ background-color: #fff3cd; border: 1px solid #ffc107; color: #856404; padding: 10px; border-radius: 4px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Password Reset Request</h2>
            </div>
            
            <div class="content">
                <p>Hello,</p>
                
                <p>You requested a password reset for your MathStep AI account.</p>
                
                <p>Click the button below to reset your password (link expires in 24 hours):</p>
                
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset My Password</a>
                </div>
                
                <p>Or copy and paste this link in your browser:</p>
                <p style="word-break: break-all; background-color: #f0f0f0; padding: 10px; border-radius: 4px;">{reset_url}</p>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong> If you did not request this, please ignore this email. Your account is secure.
                </div>
                
                <p><strong>Best regards,</strong><br/>MathStep AI Team</p>
            </div>
            
            <div class="footer">
                <p>This email was sent to {email}. Do not reply to this email.</p>
                <p>&copy; 2026 MathStep AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    email_text = f"""
Password Reset Request

Hello,

You requested a password reset for your MathStep AI account.

Click this link to reset your password (expires in 24 hours):
{reset_url}

If you did not request this, please ignore this email.

Best regards,
MathStep AI Team
    """
    
    try:
        # Create message with multipart (text + HTML)
        message = MIMEMultipart("alternative")
        message["Subject"] = email_subject
        message["From"] = settings.SMTP_FROM
        message["To"] = email
        
        # Attach plain text version
        text_part = MIMEText(email_text, "plain")
        message.attach(text_part)
        
        # Attach HTML version (preferred by email clients)
        html_part = MIMEText(email_html, "html")
        message.attach(html_part)
        
        # Send via SMTP
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, email, message.as_string())
        
        logger.info(f"Password reset email sent successfully to {email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {str(e)}. Check SMTP_USER and SMTP_PASSWORD in .env")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending password reset email to {email}: {str(e)}")
        return False
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
    
    # Validate SMTP configuration
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD or not settings.SMTP_FROM:
        logger.warning("SMTP not configured. Email verification skipped.")
        return False
    
    if not verification_url:
        verification_url = f"http://localhost:3000/verify-email"
    
    email_subject = "Verify Your Email - MathStep AI"
    
    email_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 4px; }}
            .content {{ padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 4px; margin-top: 20px; }}
            .button {{ display: inline-block; background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Welcome to MathStep AI!</h2>
            </div>
            
            <div class="content">
                <p>Thank you for signing up with us.</p>
                <p>Please verify your email address to activate your account:</p>
                
                <div style="text-align: center;">
                    <a href="{verification_url}" class="button">Verify Email</a>
                </div>
                
                <p>Or copy this link: {verification_url}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = email_subject
        message["From"] = settings.SMTP_FROM
        message["To"] = email
        
        text_part = MIMEText(f"Welcome to MathStep AI!\n\nPlease verify your email: {verification_url}", "plain")
        message.attach(text_part)
        
        html_part = MIMEText(email_html, "html")
        message.attach(html_part)
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, email, message.as_string())
        
        logger.info(f"✅ Verification email sent successfully to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        return False
