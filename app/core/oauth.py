"""
Google OAuth configuration and utilities.
"""

from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
from app.core.config import get_settings


async def verify_google_token(token: str) -> dict:
    """
    Verify and decode a Google OAuth ID token.
    
    Args:
        token: Google ID token
        
    Returns:
        Decoded token data containing user info (sub, email, name, picture, etc.)
        
    Raises:
        ValueError: If token is invalid
    """
    settings = get_settings()
    print(settings.DATABASE_URL)
    
    try:
        idinfo = verify_oauth2_token(token, Request(), settings.GOOGLE_CLIENT_ID)
        
        # Verify token wasn't revoked
        if idinfo.get("aud") != settings.GOOGLE_CLIENT_ID:
            raise ValueError("Token audience mismatch")
        
        return idinfo
    except Exception as e:
        raise ValueError(f"Invalid Google token: {str(e)}")


def get_google_login_url() -> str:
    """
    Generate Google OAuth login URL.
    
    Returns:
        URL to redirect user to for Google login
    """
    settings = get_settings()
    print(settings.DATABASE_URL)
    
    scope = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]
    
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    # Google OAuth2 authorization endpoint
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={'+'.join(scope)}&"
        f"access_type=offline"
    )
    
    return url
