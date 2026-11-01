from sqlmodel import select

from app.models import (
    Advisor,
    Course,
    CoursePlan,
    CoursePlanItem,
    Program,
    Student,
)


def login(client, username, password):
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
        },
        follow_redirects=False,
    )


def create_course_data(db):
    program = Program(
        name="Test Computer Science",
        catalog_year="2026",
        required_credits=120,
    )
    db.add(program)
    db.commit()
    db.refresh(program)

    advisor = Advisor(
        name="Test Advisor",
        email="advisor@test.com",
        department="Computer Science",
    )
    db.add(advisor)
    db.commit()
    db.refresh(advisor)

    course = Course(
        code="TEST101",
        title="Test Programming",
        credits=3,
        level="100",
        program_id=program.id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    return program, advisor, course


def test_student_can_open_dashboard(client, student_user):
    login_response = login(client, "teststudent", "StudentPass123!")

    assert login_response.status_code == 303
    assert "access_token" in client.cookies

    response = client.get("/app")

    assert response.status_code == 200


def test_student_can_open_course_planning_page(client, student_user):
    login(client, "teststudent", "StudentPass123!")

    response = client.get("/app/plan")

    assert response.status_code == 200


def test_student_can_create_course_plan(client, db, student_user):
    _, _, course = create_course_data(db)

    login(client, "teststudent", "StudentPass123!")

    response = client.post(
        "/app/plan",
        data={
            "semester": "Fall 2026",
            "course_ids": [str(course.id)],
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    plan = db.exec(
        select(CoursePlan).where(
            CoursePlan.semester == "Fall 2026"
        )
    ).first()

    assert plan is not None
    assert plan.status == "draft"

    items = db.exec(
        select(CoursePlanItem).where(
            CoursePlanItem.course_plan_id == plan.id
        )
    ).all()

    assert len(items) == 1
    assert items[0].course_id == course.id


def test_student_cannot_access_admin_dashboard(
    client, student_user
):
    login(client, "teststudent", "StudentPass123!")

    response = client.get("/admin")

    assert response.status_code == 401


def test_admin_can_open_admin_dashboard(client, admin_user):
    login(client, "testadmin", "AdminPass123!")

    response = client.get("/admin")

    assert response.status_code == 200


def test_unauthenticated_user_cannot_open_student_dashboard(client):
    response = client.get("/app")

    assert response.status_code == 401
