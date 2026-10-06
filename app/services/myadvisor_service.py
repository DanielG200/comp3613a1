from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session

from app.repositories.myadvisor import MyAdvisorRepository


class CoursePlanService:
    def __init__(self, db: Session, repo: Optional[MyAdvisorRepository] = None):
        self.db = db
        self.repo = repo or MyAdvisorRepository(db)

    def create_course_plan(self, student_id: int, advisor_id: Optional[int], semester: str, course_ids: list[int], notes: str = ""):
        if not course_ids:
            raise ValueError("Select at least one course for the semester plan")
        return self.repo.create_course_plan(student_id=student_id, advisor_id=advisor_id, semester=semester, course_ids=list(course_ids), notes=notes)

    def submit_course_plan(self, plan_id: int):
        return self.repo.submit_course_plan(plan_id)

    def revise_and_resubmit_course_plan(self, plan_id: int, course_ids: list[int]):
        if not course_ids:
            raise ValueError("Select at least one course for the semester plan")
        return self.repo.revise_and_resubmit_course_plan(plan_id, list(course_ids))

    def review_course_plan(self, plan_id: int, decision: str, notes: str, advisor_id: int):
        return self.repo.review_course_plan(plan_id=plan_id, decision=decision, notes=notes, advisor_id=advisor_id)

    def get_student_dashboard(self, student_id: int):
        student = self.repo.get_student(student_id)
        progress = self.repo.get_student_progress(student_id)
        requirements = self.repo.load_degree_requirements(student.program_id) if student and student.program_id else []
        completed_course_ids = self.repo.get_student_completed_course_ids(student_id)
        return {
            "student": student,
            "progress": progress,
            "requirements": requirements,
            "completed_course_ids": completed_course_ids,
        }

    def get_course_planning_dashboard(self, student_id: int):
        student = self.repo.get_student(student_id)
        plans = self.repo.list_course_plans_for_student(student_id)
        courses = self.repo.list_courses_for_program(student.program_id if student else None)
        return {
            "student": student,
            "plans": plans,
            "courses": courses,
        }

    def get_admin_dashboard(self):
        return {"pending": self.repo.get_pending_course_plans()}

    def get_default_program(self):
        return self.repo.ensure_default_program()

    def get_default_advisor(self):
        return self.repo.ensure_default_advisor()

    def seed_catalog(self):
        self.repo.seed_course_catalog()
