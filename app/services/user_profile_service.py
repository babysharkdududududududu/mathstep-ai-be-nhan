from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import UUID

from app.models.user import User, UserProfile
from app.models.student import Student
from app.schemas.user_profile import UserProfileResponse


def get_user_dashboard_profile(db: Session, current_user: User) -> UserProfileResponse:
    # =========================
    # 0. ENSURE UUID TYPE
    # =========================
    try:
        user_id = current_user.id if isinstance(current_user.id, UUID) else UUID(str(current_user.id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    # =========================
    # 1. FETCH DATA (BATCH - 1 QUERY EACH)
    # =========================
    student = db.execute(
        select(Student).where(Student.user_id == user_id)
    ).scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )

    profile = db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    ).scalar_one_or_none()

    # =========================
    # 2. COMPUTE XP PROGRESS
    # =========================
    xp_progress_percent = 0.0

    if student.xp_to_next_level and student.xp_to_next_level > 0:
        xp_in_level = student.xp_total % student.xp_to_next_level
        xp_progress_percent = round(
            (xp_in_level / student.xp_to_next_level) * 100, 1
        )

    # =========================
    # 3. BUILD RESPONSE
    # =========================
    return UserProfileResponse(
        # Header
        streak_days=student.streak_days,
        xp_total=student.xp_total,

        # Identity
        display_name=current_user.display_name or student.name,
        avatar_url=current_user.avatar_url,
        title=profile.title if profile else None,

        # Gamification
        level=student.level,
        xp_progress_percent=xp_progress_percent,
        xp_to_next_level=student.xp_to_next_level,
        is_pro=student.is_pro,

        # Combo
        combo_multiplier=student.combo_multiplier,
        combo_label=_resolve_combo_label(student.combo_multiplier),
    )


def _resolve_combo_label(multiplier: float) -> str:
    if multiplier >= 3.5:
        return "Đang đạt đỉnh"
    elif multiplier >= 2.0:
        return "Đang bứt phá"
    elif multiplier >= 1.5:
        return "Đang tăng tốc"
    return "Bắt đầu"