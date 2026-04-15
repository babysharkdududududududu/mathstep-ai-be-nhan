# app/api/v1/user_profile.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user_profile import UserProfileResponse
from app.services.user_profile_service import get_user_dashboard_profile
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.get(
    "/me/dashboard-profile",
    response_model=UserProfileResponse,
    summary="Lấy toàn bộ thông tin hiển thị dashboard của user hiện tại",
)
def get_dashboard_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_dashboard_profile(db, current_user)