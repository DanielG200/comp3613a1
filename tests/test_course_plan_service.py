from sqlmodel import Session, SQLModel, create_engine

from app.models import Advisor, Course, CoursePlan, CoursePlanItem, DegreeRequirement, Program, Student
from app.services.myadvisor_service import CoursePlanService


def test_course_plan_service_tracks_submission_and_decision():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        program = Program(name="Computer Science", catalog_year="2025", required_credits=120)
        session.add(program)
        session.commit()
        session.refresh(program)

        advisor = Advisor(name="Dr. Ramos", email="ramos@example.com", department="CS", role="advisor")
        session.add(advisor)
        session.commit()
        session.refresh(advisor)

        student = Student(
            name="Alice Student",
            email="alice@example.com",
            student_number="2025001",
            advisor_id=advisor.id,
            program_id=program.id,
            academic_status="Good Standing",
        )
        session.add(student)
        session.commit()
        session.refresh(student)

        course_one = Course(code="CSC101", title="Intro to Computing", credits=3, description="Intro", level="100")
        course_two = Course(code="CSC102", title="Programming I", credits=3, description="Intro", level="100")
        session.add_all([course_one, course_two])
        session.commit()
        session.refresh(course_one)
        session.refresh(course_two)

        service = CoursePlanService(session)
        plan = service.create_course_plan(
            student_id=student.id,
            advisor_id=advisor.id,
            semester="Fall 2025",
            course_ids=[course_one.id, course_two.id],
        )

        assert plan.status == "draft"
        assert len(plan.items) == 2

        service.submit_course_plan(plan.id)
        assert plan.status == "submitted"

        rejection = service.review_course_plan(plan.id, "rejected", "Choose a different elective", advisor.id)
        assert rejection.decision == "rejected"
        assert plan.status == "rejected"

        revised_plan = service.revise_and_resubmit_course_plan(plan.id, [course_two.id])
        assert revised_plan.id == plan.id
        assert revised_plan.status == "submitted"
        assert [item.course_id for item in revised_plan.items] == [course_two.id]
        assert len(revised_plan.approvals) == 1

        decision = service.review_course_plan(plan.id, "approved", "Plan meets requirements", advisor.id)
        assert decision.decision == "approved"
        assert plan.status == "approved"
        assert len(plan.approvals) == 2


def test_admin_dashboard_includes_plans_assigned_to_another_advisor():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        program = Program(name="Computer Science", catalog_year="2025", required_credits=120)
        assigned_advisor = Advisor(name="Dr. Ramos", email="ramos@example.com")
        admin_advisor = Advisor(name="Administrator", email="admin@example.com")
        session.add_all([program, assigned_advisor, admin_advisor])
        session.commit()
        session.refresh(program)
        session.refresh(assigned_advisor)

        student = Student(
            name="Alice Student",
            email="alice@example.com",
            student_number="2025001",
            advisor_id=assigned_advisor.id,
            program_id=program.id,
        )
        course = Course(code="CSC101", title="Intro to Computing", credits=3)
        session.add_all([student, course])
        session.commit()
        session.refresh(student)
        session.refresh(course)

        service = CoursePlanService(session)
        plan = service.create_course_plan(
            student_id=student.id,
            advisor_id=assigned_advisor.id,
            semester="Fall 2025",
            course_ids=[course.id],
        )
        service.submit_course_plan(plan.id)

        dashboard = service.get_admin_dashboard()

        assert [pending_plan.id for pending_plan in dashboard["pending"]] == [plan.id]


def test_student_progress_uses_course_item_status_not_plan_approval():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        program = Program(name="Computer Science", catalog_year="2025", required_credits=30)
        advisor = Advisor(name="Dr. Ramos", email="ramos@example.com", department="CS", role="advisor")
        session.add_all([program, advisor])
        session.commit()
        session.refresh(program)
        session.refresh(advisor)

        student = Student(
            name="Alice Student",
            email="alice@example.com",
            student_number="2025001",
            advisor_id=advisor.id,
            program_id=program.id,
        )
        courses = [
            Course(code="CSC101", title="Completed course", credits=3),
            Course(code="CSC102", title="In progress course", credits=6),
            Course(code="CSC103", title="Planned course", credits=3),
        ]
        session.add(student)
        session.add_all(courses)
        session.commit()
        session.refresh(student)
        for course in courses:
            session.refresh(course)
        requirements = [
            DegreeRequirement(program_id=program.id, course_id=courses[0].id, requirement_type="core", credits=3),
            DegreeRequirement(program_id=program.id, course_id=courses[2].id, requirement_type="elective", credits=3),
        ]
        session.add_all(requirements)
        session.commit()

        approved_plan = CoursePlan(student_id=student.id, advisor_id=advisor.id, semester="Fall 2025", status="approved")
        session.add(approved_plan)
        session.commit()
        session.refresh(approved_plan)
        session.add_all([
            CoursePlanItem(course_plan_id=approved_plan.id, course_id=courses[0].id, status="completed"),
            CoursePlanItem(course_plan_id=approved_plan.id, course_id=courses[1].id, status="in_progress"),
            CoursePlanItem(course_plan_id=approved_plan.id, course_id=courses[2].id, status="planned"),
        ])
        session.commit()

        dashboard = CoursePlanService(session).get_student_dashboard(student.id)
        progress = dashboard["progress"]

        assert progress["total_required_credits"] == 30
        assert progress["completed_credits"] == 3
        assert progress["in_progress_credits"] == 6
        assert progress["remaining_credits"] == 21
        assert {requirement.course_id for requirement in dashboard["requirements"]} == {courses[0].id, courses[2].id}
        assert dashboard["completed_course_ids"] == {courses[0].id}
