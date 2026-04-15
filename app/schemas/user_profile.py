# app/schemas/user_profile.py
from pydantic import BaseModel
from typing import Optional

class UserProfileResponse(BaseModel):
    # Header
    streak_days: int
    xp_total: int

    # Identity - lấy từ User trực tiếp
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    title: Optional[str] = None        # từ UserProfile nếu có, không thì None

    # Gamification
    level: int
    xp_progress_percent: float
    xp_to_next_level: int
    is_pro: bool

    # Combo
    combo_multiplier: float
    combo_label: str

    # Achievement
    current_achievement_name: Optional[str] = None
    current_achievement_desc: Optional[str] = None
    current_achievement_progress: Optional[int] = None
    current_achievement_total: Optional[int] = None

    class Config:
        from_attributes = True