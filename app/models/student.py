"""
Student model.
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, func, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.db.base import Base


class Student(Base):
    """Student model."""
    __tablename__ = "students"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id          = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                              nullable=False, unique=True, index=True)

    # ── Identity ──────────────────────────────────────────────────────────────
    name             = Column(String(80), nullable=True)
    grade_level      = Column(String(20), nullable=True)   # "Lớp 8", "Grade 9", …

    # ── Gamification ──────────────────────────────────────────────────────────
    level            = Column(Integer, default=1,    nullable=False)
    xp_total         = Column(Integer, default=0,    nullable=False)
    xp_to_next_level = Column(Integer, default=1000, nullable=False)  # threshold

    streak_days      = Column(Integer, default=0,    nullable=False)
    last_active_date = Column(DateTime(timezone=True), nullable=True)  # for streak calc

    combo_multiplier = Column(Float,   default=1.0,  nullable=False)   # 1.0 → 3.5
    combo_expires_at = Column(DateTime(timezone=True), nullable=True)

    # ── Subscription flag (fast read) ─────────────────────────────────────────
    is_pro           = Column(Boolean, default=False, nullable=False)

    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="student")

    def __repr__(self):
        return (f"<Student id={self.id} name={self.name} "
                f"lv={self.level} xp={self.xp_total}>")
