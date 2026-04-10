from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.setup import OnboardingStudentRequest
from app.models.user import User
from app.services.setup_service import onboard_student
from app.utils.dependencies import get_current_user


router = APIRouter()

@router.put("/onboarding/student")
def onboarding_student(
    request: OnboardingStudentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = onboard_student(db, current_user, request)

    return {
        "status": "success",
        "data": {
            "student_id": str(student.id),
            "grade_level": student.grade_level
        }
    }