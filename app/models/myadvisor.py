from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Program(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    catalog_year: str = "2025"
    required_credits: int = 120

    students: list["Student"] = Relationship(back_populates="program")
    courses: list["Course"] = Relationship(back_populates="program")
    requirements: list["DegreeRequirement"] = Relationship(back_populates="program")


class Advisor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    department: str = "Academic Advising"
    role: str = "advisor"

    students: list["Student"] = Relationship(back_populates="advisor")
    plans: list["CoursePlan"] = Relationship(back_populates="advisor")
    approvals: list["Approval"] = Relationship(back_populates="advisor")


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    student_number: str = Field(index=True, unique=True)
    advisor_id: Optional[int] = Field(default=None, foreign_key="advisor.id")
    program_id: Optional[int] = Field(default=None, foreign_key="program.id")
    academic_status: str = "Good Standing"

    advisor: Optional["Advisor"] = Relationship(back_populates="students")
    program: Optional["Program"] = Relationship(back_populates="students")
    plans: list["CoursePlan"] = Relationship(back_populates="student")


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    title: str
    credits: int
    description: str = ""
    level: str = "100"
    program_id: Optional[int] = Field(default=None, foreign_key="program.id")

    program: Optional["Program"] = Relationship(back_populates="courses")
    requirements: list["DegreeRequirement"] = Relationship(back_populates="course")
    plan_items: list["CoursePlanItem"] = Relationship(back_populates="course")


class DegreeRequirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    program_id: int = Field(foreign_key="program.id")
    course_id: int = Field(foreign_key="course.id")
    requirement_type: str = "core"
    credits: int = 3

    program: Optional["Program"] = Relationship(back_populates="requirements")
    course: Optional["Course"] = Relationship(back_populates="requirements")


class CoursePlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    advisor_id: Optional[int] = Field(default=None, foreign_key="advisor.id")
    semester: str = "Fall 2025"
    status: str = "draft"
    notes: str = ""
    submitted_at: Optional[datetime] = Field(default=None)
    reviewed_at: Optional[datetime] = Field(default=None)

    student: Optional["Student"] = Relationship(back_populates="plans")
    advisor: Optional["Advisor"] = Relationship(back_populates="plans")
    items: list["CoursePlanItem"] = Relationship(back_populates="course_plan")
    approvals: list["Approval"] = Relationship(back_populates="course_plan")


class CoursePlanItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course_plan_id: int = Field(foreign_key="courseplan.id")
    course_id: int = Field(foreign_key="course.id")
    priority: str = "required"
    status: str = "planned"

    course_plan: Optional["CoursePlan"] = Relationship(back_populates="items")
    course: Optional["Course"] = Relationship(back_populates="plan_items")


class Approval(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course_plan_id: int = Field(foreign_key="courseplan.id")
    advisor_id: int = Field(foreign_key="advisor.id")
    decision: str = "pending"
    notes: str = ""
    approved_at: Optional[datetime] = Field(default=None)

    advisor: Optional["Advisor"] = Relationship(back_populates="approvals")
    course_plan: Optional["CoursePlan"] = Relationship(back_populates="approvals")
