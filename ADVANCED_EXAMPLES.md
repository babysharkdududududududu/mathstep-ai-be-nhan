"""
Advanced Usage Patterns & Code Examples

This file demonstrates advanced patterns for using the authentication system.
"""

# ============================================================================
# 1. ROLE-BASED ENDPOINTS
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from app.utils.dependencies import get_current_user, get_student_user, get_parent_user
from app.models.user import User
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()


@router.get("/student/dashboard")
def student_dashboard(current_user: User = Depends(get_student_user)):
    """
    Example: Student-only endpoint
    
    Only users with role=STUDENT can access this.
    """
    return {
        "message": "Welcome to student dashboard",
        "user_id": str(current_user.id),
        "email": current_user.email
    }


@router.get("/parent/dashboard")
def parent_dashboard(current_user: User = Depends(get_parent_user)):
    """
    Example: Parent-only endpoint
    
    Only users with role=PARENT can access this.
    """
    return {
        "message": "Welcome to parent dashboard",
        "user_id": str(current_user.id),
        "email": current_user.email
    }


@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Example: Endpoint accessible by any authenticated user
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat()
    }


# ============================================================================
# 2. ACCESSING RELATED DATA
# ============================================================================

from app.models.student import Student
from app.models.parent import Parent


@router.get("/student/profile")
def get_student_profile(
    current_user: User = Depends(get_student_user),
    db: Session = Depends(get_db)
):
    """
    Example: Get student information
    """
    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    return {
        "user_id": str(student.user_id),
        "student_id": str(student.id),
        "name": student.name,
        "grade_level": student.grade_level,
        "email": current_user.email
    }


@router.get("/parent/profile")
def get_parent_profile(
    current_user: User = Depends(get_parent_user),
    db: Session = Depends(get_db)
):
    """
    Example: Get parent information
    """
    parent = db.query(Parent).filter(
        Parent.user_id == current_user.id
    ).first()
    
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent profile not found"
        )
    
    return {
        "user_id": str(parent.user_id),
        "parent_id": str(parent.id),
        "name": parent.name,
        "email": current_user.email
    }


# ============================================================================
# 3. UPDATING USER INFORMATION
# ============================================================================

from pydantic import BaseModel


class UpdateStudentRequest(BaseModel):
    """Schema for updating student info"""
    name: str | None = None
    grade_level: str | None = None


@router.put("/student/profile")
def update_student_profile(
    request: UpdateStudentRequest,
    current_user: User = Depends(get_student_user),
    db: Session = Depends(get_db)
):
    """
    Example: Update student profile
    """
    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Update fields if provided
    if request.name is not None:
        student.name = request.name
    if request.grade_level is not None:
        student.grade_level = request.grade_level
    
    db.commit()
    db.refresh(student)
    
    return {
        "message": "Profile updated successfully",
        "name": student.name,
        "grade_level": student.grade_level
    }


# ============================================================================
# 4. CUSTOM AUTHENTICATION LOGIC
# ============================================================================

from app.core.security import hash_password, verify_password


class ChangePasswordRequest(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str


@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Example: Change user password
    """
    # Verify current password
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for OAuth users"
        )
    
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters"
        )
    
    if request.new_password == request.current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    current_user.password_hash = hash_password(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


# ============================================================================
# 5. CONDITIONAL ENDPOINT ACCESS
# ============================================================================

def verify_student_ownership(
    student_id: str,
    current_user: User = Depends(get_student_user),
    db: Session = Depends(get_db)
) -> Student:
    """
    Dependency: Verify current user owns the student record
    """
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if student.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this student record"
        )
    
    return student


@router.get("/student/{student_id}")
def get_student_by_id(
    student: Student = Depends(verify_student_ownership)
):
    """
    Example: Get specific student (only if owner)
    """
    return {
        "id": str(student.id),
        "name": student.name,
        "grade_level": student.grade_level
    }


# ============================================================================
# 6. ADMIN-LIKE OPERATIONS (For future use)
# ============================================================================

from typing import Optional


@router.get("/admin/users", tags=["admin"])
def list_all_users(
    role: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Example: List all users (admin endpoint)
    
    Note: Add role checking in production
    """
    # TODO: Add admin role check
    # if current_user.role != "ADMIN":
    #     raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.all()
    
    return {
        "total": len(users),
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "role": u.role,
                "created_at": u.created_at.isoformat()
            }
            for u in users
        ]
    }


@router.get("/admin/stats", tags=["admin"])
def get_system_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Example: Get system statistics
    """
    total_users = db.query(User).count()
    total_students = db.query(Student).count()
    total_parents = db.query(Parent).count()
    students_with_oauth = db.query(User).filter(
        User.role == "STUDENT",
        User.google_id.isnot(None)
    ).count()
    
    return {
        "total_users": total_users,
        "total_students": total_students,
        "total_parents": total_parents,
        "students_with_oauth": students_with_oauth,
        "oauth_adoption_rate": (
            f"{(students_with_oauth / total_students * 100):.1f}%"
            if total_students > 0 else "0%"
        )
    }


# ============================================================================
# 7. ERROR HANDLING PATTERNS
# ============================================================================

from fastapi import status


class CustomException(Exception):
    """Base exception for custom errors"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


@router.post("/protected-operation")
def protected_operation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Example: Error handling patterns
    """
    try:
        # Simulate some operation
        if not current_user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email not set"
            )
        
        # Operation succeeded
        return {
            "status": "success",
            "message": "Operation completed"
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Catch unexpected errors
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


# ============================================================================
# 8. PAGINATION EXAMPLE
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = 0
    limit: int = 10


@router.get("/students/list")
def list_students(
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Example: Paginated list of students
    """
    query = db.query(Student)
    total = query.count()
    
    students = query.offset(params.skip).limit(params.limit).all()
    
    return {
        "total": total,
        "skip": params.skip,
        "limit": params.limit,
        "items": [
            {
                "id": str(s.id),
                "name": s.name,
                "grade_level": s.grade_level
            }
            for s in students
        ]
    }


# ============================================================================
# 9. BACKGROUND TASKS EXAMPLE
# ============================================================================

from fastapi import BackgroundTasks
from datetime import datetime


def send_welcome_email(email: str, name: str):
    """Background task: Send welcome email"""
    print(f"Sending welcome email to {email} ({name})")
    # Implement actual email sending here


@router.post("/register-with-email")
def register_with_email(
    email: str,
    name: str,
    background_tasks: BackgroundTasks
):
    """
    Example: Register and send email in background
    """
    # Register user (logic here)
    
    # Add background task
    background_tasks.add_task(send_welcome_email, email, name)
    
    return {"message": "Registration successful. Welcome email will be sent shortly."}


# ============================================================================
# 10. TRANSACTION EXAMPLE
# ============================================================================

from sqlalchemy import event


@router.post("/batch-register-students")
def batch_register_students(
    students_data: list[dict],
    db: Session = Depends(get_db)
):
    """
    Example: Batch operation with transaction handling
    """
    try:
        created_students = []
        
        for data in students_data:
            # Create user
            user = User(email=data["email"], role="STUDENT")
            db.add(user)
            db.flush()
            
            # Create student
            student = Student(
                user_id=user.id,
                name=data.get("name")
            )
            db.add(student)
            
            created_students.append({
                "user_id": str(user.id),
                "student_id": str(student.id),
                "email": user.email
            })
        
        # Commit all changes in one transaction
        db.commit()
        
        return {
            "message": f"Created {len(created_students)} students",
            "students": created_students
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch registration failed: {str(e)}"
        )


# ============================================================================
# TESTING EXAMPLES
# ============================================================================

"""
Using pytest for testing:

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_student():
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "role": "STUDENT"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login():
    # Register first
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "role": "STUDENT"
    })
    
    # Login
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_current_user(client, auth_token):
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_student_only_endpoint(client, auth_token):
    response = client.get(
        "/student/dashboard",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
"""
