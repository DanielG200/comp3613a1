from fastapi import HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.myadvisor import MyAdvisorRepository
from app.services.myadvisor_service import CoursePlanService
from app.utilities.flash import flash
from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    repo = MyAdvisorRepository(db)
    service = CoursePlanService(db, repo)
    student = repo.ensure_student_record(user)
    dashboard = service.get_student_dashboard(student.id)

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={
            "user": user,
            "student": dashboard["student"],
            "progress": dashboard["progress"],
            "requirements": dashboard["requirements"],
            "completed_course_ids": dashboard["completed_course_ids"],
        },
    )


@router.get("/app/plan", response_class=HTMLResponse)
async def plan_courses_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    repo = MyAdvisorRepository(db)
    service = CoursePlanService(db, repo)
    student = repo.ensure_student_record(user)
    dashboard = service.get_course_planning_dashboard(student.id)

    return templates.TemplateResponse(
        request=request,
        name="plan_courses.html",
        context={
            "user": user,
            "student": dashboard["student"],
            "plans": dashboard["plans"],
            "courses": dashboard["courses"],
        },
    )


@router.post("/app/plan", response_class=HTMLResponse)
async def create_course_plan(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    semester: str = Form(...),
    course_ids: list[str] = Form(...),
):
    repo = MyAdvisorRepository(db)
    service = CoursePlanService(db, repo)
    student = repo.ensure_student_record(user)
    try:
        selected_ids = [int(course_id) for course_id in course_ids if course_id]
        plan = service.create_course_plan(
            student_id=student.id,
            advisor_id=student.advisor_id,
            semester=semester,
            course_ids=selected_ids,
        )
        flash(request, f"Course plan for {plan.semester} saved as a draft.", "success")
    except ValueError as exc:
        flash(request, str(exc), "danger")

    return RedirectResponse(url=request.url_for("plan_courses_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/plan/{plan_id}/submit", response_class=HTMLResponse)
async def submit_course_plan(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    plan_id: int,
):
    repo = MyAdvisorRepository(db)
    service = CoursePlanService(db, repo)
    student = repo.ensure_student_record(user)
    plan = repo.get_course_plan(plan_id)

    if plan is None or plan.student_id != student.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course plan not found")

    service.submit_course_plan(plan_id)
    flash(request, "Course plan submitted for review.", "success")
    return RedirectResponse(url=request.url_for("plan_courses_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/app/plan/{plan_id}/revise", response_class=HTMLResponse)
async def revise_course_plan(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    plan_id: int,
    course_ids: list[str] = Form(...),
):
    repo = MyAdvisorRepository(db)
    service = CoursePlanService(db, repo)
    student = repo.ensure_student_record(user)
    plan = repo.get_course_plan(plan_id)

    if plan is None or plan.student_id != student.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course plan not found")

    try:
        selected_ids = [int(course_id) for course_id in course_ids if course_id]
        service.revise_and_resubmit_course_plan(plan_id, selected_ids)
        flash(request, "Revised course plan resubmitted for review.", "success")
    except ValueError as exc:
        flash(request, str(exc), "danger")

    return RedirectResponse(url=request.url_for("plan_courses_view"), status_code=status.HTTP_303_SEE_OTHER)
