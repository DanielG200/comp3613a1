"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.myadvisor import (
    Advisor,
    Approval,
    Course,
    CoursePlan,
    CoursePlanItem,
    DegreeRequirement,
    Program,
    Student,
)
from app.models.user import User

__all__ = [
    "Advisor",
    "Approval",
    "Course",
    "CoursePlan",
    "CoursePlanItem",
    "DegreeRequirement",
    "Program",
    "Student",
    "User",
]
