from pydantic import BaseModel
from typing import Literal

class OnboardingStudentRequest(BaseModel):
    grade_level: Literal[
        "Grade 6","Grade 7","Grade 8","Grade 9",
        "Grade 10","Grade 11","Grade 12"
    ]