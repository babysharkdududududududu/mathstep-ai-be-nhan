"""
Authentication service with business logic.
"""
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.parent import Parent
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
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
        
        # Hash password
        password_hash = hash_password(request.password)
        
        if len(request.password.encode('utf-8')) > 72:
            raise HTTPException(
                status_code=400,
                detail="Password too long (max 72 bytes for bcrypt)."
            )
        
        try:
            # Create User
            user = User(
                email=request.email,
                password_hash=password_hash,
                role=UserRole(request.role)
            )
            db.add(user)
            db.flush()  # Flush to get the user ID
            
            
            # Create corresponding entity based on role
            if request.role == "STUDENT":
                student = Student(
                    user_id=user.id,
                    name=f"{request.firstName} {request.lastName}"
                )
                db.add(student)

            elif request.role == "PARENT":
                parent = Parent(
                    user_id=user.id,
                    name=f"{request.firstName} {request.lastName}"
                )
                db.add(parent)
            
            db.commit()
            db.refresh(user)
            
            # Create token
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email, "role": user.role}
            )
            
            return TokenResponse(
                access_token=access_token,
                user_id=user.id,
                email=user.email,
                role=user.role
            )
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered."
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
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
        
        # Create token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        
        return TokenResponse(
            access_token=access_token,
            user_id=user.id,
            email=user.email,
            role=user.role
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
                    data={"sub": str(user.id), "email": user.email, "role": user.role}
                )
                return TokenResponse(
                    access_token=access_token,
                    user_id=user.id,
                    email=user.email,
                    role=user.role
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
            
            # Create token
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email, "role": user.role}
            )
            
            return TokenResponse(
                access_token=access_token,
                user_id=user.id,
                email=user.email,
                role=user.role
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


