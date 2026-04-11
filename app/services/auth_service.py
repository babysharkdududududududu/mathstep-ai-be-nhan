"""
Authentication service with business logic.
"""
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.parent import Parent
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token
)
from fastapi import HTTPException, status


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def register_user(
        db: Session,
        request: RegisterRequest
    ) -> TokenResponse:
       
        # Validate role
        if request.role not in ["STUDENT", "PARENT"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be STUDENT or PARENT."
            )
        
        # Validate password length in bytes (bcrypt limit is 72 bytes)
        if len(request.password.encode('utf-8')) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password too long (max 72 bytes for bcrypt)."
            )
        
        # Hash password
        password_hash = hash_password(request.password)
        
        try:
            # Create User
            user = User(
                email=request.email,
                password_hash=password_hash,
                role=UserRole(request.role)
            )
            db.add(user)
            db.flush()  # Flush to get the user ID
            
            # Get full name from request
            full_name = request.get_full_name()
            
            # Create corresponding entity based on role
            if request.role == "STUDENT":
                student = Student(
                    user_id=user.id,
                    name=full_name
                )
                db.add(student)

            elif request.role == "PARENT":
                parent = Parent(
                    user_id=user.id,
                    name=full_name
                )
                db.add(parent)
            
            db.commit()
            db.refresh(user)
            
            # Create tokens
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email, "role": user.role.value}
            )
            
            refresh_token = create_refresh_token(
                data={"sub": str(user.id), "email": user.email}
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user_id=user.id,
                email=user.email,
                role=user.role.value
            )
            
        except IntegrityError as e:
            db.rollback()
            if "email" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered."
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Registration failed: duplicate entry."
            )
        except Exception as e:
            db.rollback()
            # Don't expose internal error details in production
            import traceback
            traceback.print_exc()  # Log for debugging
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed. Please try again."
            )
    
    @staticmethod
    def login_user(
        db: Session,
        request: LoginRequest
    ) -> TokenResponse:
        """
        Authenticate user and return JWT token.
        
        Args:
            db: Database session
            request: Login request data
            
        Returns:
            Token response with JWT
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )
        
        # Check if password is set (not OAuth user)
        if not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This account uses Google login. Please use Google to sign in."
            )
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value}
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            email=user.email,
            role=user.role.value
        )
    
    @staticmethod
    def google_login_or_create(
        db: Session,
        google_id: str,
        email: str,
        name: Optional[str] = None
    ) -> TokenResponse:
        """
        Handle Google OAuth login. Create user if not exists.
        
        Default role for new users is STUDENT.
        
        Args:
            db: Database session
            google_id: Google user ID
            email: Google email
            name: Google name (optional)
            
        Returns:
            Token response with JWT
            
        Raises:
            HTTPException: If database operation fails
        """
        try:
            # Check if user exists by google_id
            user = db.query(User).filter(User.google_id == google_id).first()
            
            if user:
                # User exists, login
                access_token = create_access_token(
                    data={"sub": str(user.id), "email": user.email, "role": user.role.value}
                )
                refresh_token = create_refresh_token(
                    data={"sub": str(user.id), "email": user.email}
                )
                return TokenResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    user_id=user.id,
                    email=user.email,
                    role=user.role.value
                )
            
            # User doesn't exist, create new
            # Default role is STUDENT for Google OAuth
            user = User(
                email=email,
                google_id=google_id,
                role=UserRole.STUDENT  # Default role
            )
            db.add(user)
            db.flush()
            
            # Create Student record (default role)
            student = Student(user_id=user.id, name=name)
            db.add(student)
            
            db.commit()
            db.refresh(user)
            
            # Create tokens
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email, "role": user.role.value}
            )
            
            refresh_token = create_refresh_token(
                data={"sub": str(user.id), "email": user.email}
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user_id=user.id,
                email=user.email,
                role=user.role.value
            )
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered with another method."
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Google login failed: {str(e)}"
            )
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID (UUID as string)
            
        Returns:
            User object or None if not found
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def forgot_password(
        db: Session,
        email: str
    ) -> dict:
        """
        Handle forgot password request.
        Generates a reset token and sends email.
        
        Args:
            db: Database session
            email: User email address
            
        Returns:
            Dictionary with status message
            
        Raises:
            HTTPException: If email not found
        """
        from app.utils.password_reset import create_password_reset_token
        from app.utils.email import send_password_reset_email
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists (security best practice)
            # Still return success for privacy
            return {
                "message": "If an account exists with this email, a password reset link has been sent."
            }
        
        try:
            # Create reset token
            reset_token = create_password_reset_token(db, str(user.id))
            
            # Send email
            email_sent = send_password_reset_email(email, reset_token)
            
            if not email_sent:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send reset email. Please try again."
                )
            
            return {
                "message": "Password reset link sent to your email."
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process password reset request."
            )
    
    @staticmethod
    def reset_password(
        db: Session,
        token: str,
        new_password: str
    ) -> dict:
        """
        Handle password reset.
        
        Args:
            db: Database session
            token: Reset token from email
            new_password: New password
            
        Returns:
            Dictionary with success message
            
        Raises:
            HTTPException: If token invalid or password reset fails
        """
        from app.utils.password_reset import verify_reset_token, invalidate_reset_tokens
        
        # Validate password length
        if len(new_password.encode('utf-8')) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password too long (max 72 bytes for bcrypt)."
            )
        
        # Verify token
        reset_token = verify_reset_token(db, token)
        
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired reset token."
            )
        
        try:
            # Get user
            user = db.query(User).filter(User.id == reset_token.user_id).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found."
                )
            
            # Hash new password
            new_password_hash = hash_password(new_password)
            
            # Update password
            user.password_hash = new_password_hash
            
            # Mark token as used
            reset_token.mark_as_used()
            
            # Invalidate all other reset tokens for this user
            invalidate_reset_tokens(db, str(user.id))
            
            db.commit()
            
            return {"message": "Password reset successful. Please login with your new password."}
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password. Please try again."
            )
    
    @staticmethod
    def refresh_token(
        db: Session,
        refresh_token_str: str
    ) -> TokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            db: Database session
            refresh_token_str: Refresh token from request
            
        Returns:
            New token response with fresh access token
            
        Raises:
            HTTPException: If refresh token invalid or expired
        """
        # Decode refresh token
        payload = decode_refresh_token(refresh_token_str)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token."
            )
        
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token."
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        
        # Create new access token
        new_access_token = create_access_token(
            data={"sub": user_id, "email": user.email, "role": user.role.value}
        )
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token_str,  # Return same refresh token
            user_id=user.id,
            email=user.email,
            role=user.role.value
        )
