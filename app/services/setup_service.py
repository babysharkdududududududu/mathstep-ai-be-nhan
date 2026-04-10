

from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.parent import Parent
from fastapi import HTTPException, status
from app.schemas.setup import OnboardingStudentRequest

def onboard_student(
    db: Session,
    user: User,
    request: OnboardingStudentRequest
):
    if user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can perform onboarding"
        )

    student = db.query(Student).filter(
        Student.user_id == user.id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    try:
        student.grade_level = request.grade_level
        db.commit()
        db.refresh(student)
    except Exception:
        db.rollback()
        raise

    return student