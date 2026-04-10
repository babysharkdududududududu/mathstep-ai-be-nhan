"""
Authentication API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx
from app.db.session import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    GoogleLoginRequest,
    TokenResponse,
    UserResponse
)
from app.services.auth_service import AuthService
from app.core.config import get_settings
from app.core.oauth import get_google_login_url, verify_google_token
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
print(settings.DATABASE_URL)


@router.post("/register", response_model=TokenResponse)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Register a new user.
    
    Creates a User and corresponding Student or Parent entity based on role.
    
    Query Parameters:
        - email: User email (required, must be unique)
        - password: Password (required, minimum 8 characters)
        - role: User role (required, must be STUDENT or PARENT)
    
    Returns:
        Token response with JWT access token
    """
    return AuthService.register_user(db, request)


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Authenticate user and return JWT token.
    
    Verifies email and password, then returns access token.
    
    Query Parameters:
        - email: User email (required)
        - password: User password (required)
    
    Returns:
        Token response with JWT access token
    """
    return AuthService.login_user(db, request)


@router.get("/google/login")
def google_login() -> RedirectResponse:
    """
    Redirect to Google OAuth login.
    
    Returns:
        Redirect to Google OAuth consent screen
    """
    url = get_google_login_url()
    return RedirectResponse(url=url)


@router.get("/google/callback")
async def google_callback(
    code: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Handle Google OAuth callback.
    
    Exchanges authorization code for ID token, retrieves user info,
    and creates or logs in user.
    
    Query Parameters:
        - code: Authorization code from Google
    
    Returns:
        Token response with JWT access token
    """
    try:
        # Exchange code for token
        token_url = "https://oauth2.googleapis.com/token"
        
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_data)
            response.raise_for_status()
            token_response = response.json()
        
        id_token = token_response.get("id_token")
        
        if not id_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get ID token from Google."
            )
        
        # Verify token and get user info
        user_info = await verify_google_token(id_token)
        
        google_id = user_info.get("sub")
        email = user_info.get("email")
        name = user_info.get("name")
        
        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google."
            )
        
        # Create or login user
        token_response = AuthService.google_login_or_create(
            db=db,
            google_id=google_id,
            email=email,
            name=name
        )
        
        return token_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google login failed: {str(e)}"
        )


@router.post("/google/login", response_model=TokenResponse)
async def google_login_with_token(
    request: GoogleLoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    try:
        user_info = await verify_google_token(request.token)

        google_id = user_info.get("sub")
        email = user_info.get("email")
        name = user_info.get("name")

        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google token."
            )

        token_response = AuthService.google_login_or_create(
            db=db,
            google_id=google_id,
            email=email,
            name=name
        )

        return token_response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    Get current authenticated user info.
    
    Requires valid JWT token.
    
    Returns:
        Current user information
    """
    return current_user
