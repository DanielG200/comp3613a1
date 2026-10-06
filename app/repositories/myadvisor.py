from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from app.models import Advisor, Approval, Course, CoursePlan, CoursePlanItem, DegreeRequirement, Program, Student


class MyAdvisorRepository:
    def __init__(self, db: Session):
        self.db = db

    def ensure_default_program(self) -> Program:
        program = self.db.exec(select(Program).where(Program.name == "BSc Computer Science")).one_or_none()
        if program is not None:
            return program

        program = Program(name="BSc Computer Science", catalog_year="2025", required_credits=120)
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        return program

    def ensure_default_advisor(self) -> Advisor:
        advisor = self.db.exec(select(Advisor).where(Advisor.email == "advisor@example.com")).one_or_none()
        if advisor is not None:
            return advisor

        advisor = Advisor(name="Dr. Ramos", email="advisor@example.com", department="Computer Science", role="advisor")
        self.db.add(advisor)
        self.db.commit()
        self.db.refresh(advisor)
        return advisor

    def ensure_student_record(self, user) -> Student:
        student = self.db.exec(select(Student).where(Student.email == user.email)).one_or_none()
        if student is not None:
            return student

        program = self.ensure_default_program()
        advisor = self.ensure_default_advisor()
        student = Student(
            name=user.username,
            email=user.email,
            student_number=f"ST{user.id or 1000}",
            advisor_id=advisor.id,
            program_id=program.id,
            academic_status="Good Standing",
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def ensure_advisor_record(self, user) -> Advisor:
        advisor = self.db.exec(select(Advisor).where(Advisor.email == user.email)).one_or_none()
        if advisor is not None:
            return advisor

        advisor = Advisor(name=user.username, email=user.email, department="Academic Advising", role="advisor")
        self.db.add(advisor)
        self.db.commit()
        self.db.refresh(advisor)
        return advisor

    def get_student(self, student_id: int) -> Optional[Student]:
        return self.db.get(Student, student_id)

    def get_advisor(self, advisor_id: int) -> Optional[Advisor]:
        return self.db.get(Advisor, advisor_id)

    def get_student_by_email(self, email: str) -> Optional[Student]:
        return self.db.exec(select(Student).where(Student.email == email)).one_or_none()

    def get_advisor_by_email(self, email: str) -> Optional[Advisor]:
        return self.db.exec(select(Advisor).where(Advisor.email == email)).one_or_none()

    def list_courses_for_program(self, program_id: Optional[int] = None) -> list[Course]:
        query = select(Course)
        if program_id is not None:
            query = query.where(Course.program_id == program_id)
        return self.db.exec(query).all()

    def load_degree_requirements(self, program_id: int) -> list[DegreeRequirement]:
        return self.db.exec(select(DegreeRequirement).where(DegreeRequirement.program_id == program_id)).all()

    def get_student_completed_course_ids(self, student_id: int) -> set[int]:
        return set(self.db.exec(
            select(CoursePlanItem.course_id)
            .join(CoursePlan)
            .where(CoursePlan.student_id == student_id, CoursePlanItem.status == "completed")
        ).all())

    def get_student_progress(self, student_id: int) -> dict:
        student = self.get_student(student_id)
        if student is None or student.program is None:
            return {"total_required_credits": 0, "completed_credits": 0, "remaining_credits": 0, "percent": 0, "plan_status": "No program assigned"}

        total_required = student.program.required_credits
        item_credits = self.db.exec(
            select(CoursePlanItem.status, Course.credits)
            .join(CoursePlan)
            .join(Course)
            .where(
                CoursePlan.student_id == student_id,
                CoursePlanItem.status.in_(["completed", "in_progress"]),
            )
        ).all()
        completed_credits = sum(credits for item_status, credits in item_credits if item_status == "completed")
        in_progress_credits = sum(credits for item_status, credits in item_credits if item_status == "in_progress")
        remaining = total_required - completed_credits - in_progress_credits
        percent = round((completed_credits / total_required) * 100) if total_required else 0
        return {
            "total_required_credits": total_required,
            "completed_credits": completed_credits,
            "in_progress_credits": in_progress_credits,
            "remaining_credits": remaining,
            "percent": percent,
            "plan_status": "On track" if percent >= 40 else "Needs attention",
        }

    def create_course_plan(self, student_id: int, advisor_id: Optional[int], semester: str, course_ids: list[int], notes: str = "") -> CoursePlan:
        plan = CoursePlan(student_id=student_id, advisor_id=advisor_id, semester=semester, status="draft", notes=notes)
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        for position, course_id in enumerate(course_ids, start=1):
            item = CoursePlanItem(course_plan_id=plan.id, course_id=course_id, priority="required" if position == 1 else "elective", status="planned")
            self.db.add(item)

        self.db.commit()
        self.db.refresh(plan)
        return plan

    def submit_course_plan(self, plan_id: int) -> CoursePlan:
        plan = self.db.get(CoursePlan, plan_id)
        if plan is None:
            raise ValueError("Course plan not found")
        if plan.status != "draft":
            raise ValueError("Only draft course plans can be submitted")
        plan.status = "submitted"
        plan.submitted_at = datetime.utcnow()
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def review_course_plan(self, plan_id: int, decision: str, notes: str, advisor_id: int) -> Approval:
        plan = self.db.get(CoursePlan, plan_id)
        if plan is None:
            raise ValueError("Course plan not found")
        if plan.status != "submitted":
            raise ValueError("Only submitted course plans can be reviewed")

        decision_text = decision.lower().strip()
        if decision_text not in {"approved", "rejected"}:
            raise ValueError("Decision must be approved or rejected")

        approval = Approval(
            course_plan_id=plan.id,
            advisor_id=advisor_id,
            decision=decision_text,
            notes=notes,
            approved_at=datetime.utcnow(),
        )
        self.db.add(approval)

        plan.status = decision_text
        plan.reviewed_at = datetime.utcnow()
        plan.notes = notes
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(approval)
        self.db.refresh(plan)
        return approval

    def revise_and_resubmit_course_plan(self, plan_id: int, course_ids: list[int]) -> CoursePlan:
        plan = self.db.get(CoursePlan, plan_id)
        if plan is None:
            raise ValueError("Course plan not found")
        if plan.status != "rejected":
            raise ValueError("Only rejected course plans can be revised")

        for item in plan.items:
            self.db.delete(item)
        for position, course_id in enumerate(course_ids, start=1):
            item = CoursePlanItem(
                course_plan_id=plan.id,
                course_id=course_id,
                priority="required" if position == 1 else "elective",
                status="planned",
            )
            self.db.add(item)

        plan.status = "submitted"
        plan.submitted_at = datetime.utcnow()
        plan.reviewed_at = None
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def get_pending_course_plans(self) -> list[CoursePlan]:
        return self.db.exec(
            select(CoursePlan)
            .where(CoursePlan.status == "submitted")
            .order_by(CoursePlan.submitted_at.desc())
        ).all()

    def get_course_plan(self, plan_id: int) -> Optional[CoursePlan]:
        return self.db.get(CoursePlan, plan_id)

    def list_course_plans_for_student(self, student_id: int) -> list[CoursePlan]:
        return self.db.exec(select(CoursePlan).where(CoursePlan.student_id == student_id).order_by(CoursePlan.submitted_at.desc())).all()

    def get_all_course_plans(self) -> list[CoursePlan]:
        return self.db.exec(select(CoursePlan)).all()

    def seed_course_catalog(self) -> None:
        program = self.ensure_default_program()
        existing = self.db.exec(select(Course).where(Course.program_id == program.id)).all()
        if existing:
            return

        offerings = [
            ("CSC101", "Introduction to Computing", 3, "Foundations of computing", "100"),
            ("CSC102", "Programming I", 3, "Introductory programming", "100"),
            ("CSC201", "Data Structures", 3, "Core data structures", "200"),
            ("CSC210", "Discrete Mathematics", 3, "Logic and proof", "200"),
            ("CSC301", "Algorithms", 3, "Design and analysis", "300"),
            ("CSC320", "Operating Systems", 3, "System design", "300"),
        ]
        for code, title, credits, desc, level in offerings:
            course = Course(code=code, title=title, credits=credits, description=desc, level=level, program_id=program.id)
            self.db.add(course)

        required_courses = [
            ("CSC101", "core"),
            ("CSC102", "core"),
            ("CSC201", "core"),
            ("CSC210", "core"),
            ("CSC301", "core"),
        ]
        for code, requirement_type in required_courses:
            course = self.db.exec(select(Course).where(Course.code == code)).one()
            req = DegreeRequirement(program_id=program.id, course_id=course.id, requirement_type=requirement_type, credits=course.credits)
            self.db.add(req)

        self.db.commit()
