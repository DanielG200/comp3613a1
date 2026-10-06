from fastapi import Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AdminDep
from app.dependencies.session import SessionDep
from app.repositories.myadvisor import MyAdvisorRepository
from app.services.myadvisor_service import CoursePlanService
from app.utilities.flash import flash
from . import router, templates


@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db: SessionDep,
):
    repo = MyAdvisorRepository(db)
    service = CoursePlanService(db, repo)
    dashboard = service.get_admin_dashboard()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "user": user,
            "pending": dashboard["pending"],
        },
    )


@router.get("/admin/plan/{plan_id}", response_class=HTMLResponse)
async def admin_plan_view(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    plan_id: int,
):
    repo = MyAdvisorRepository(db)
    plan = repo.get_course_plan(plan_id)

    if plan is None or plan.status != "submitted":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submitted course plan not found")

    return templates.TemplateResponse(
        request=request,
        name="admin_plan.html",
        context={"user": user, "plan": plan},
    )


@router.post("/admin/plan/{plan_id}/decision", response_class=HTMLResponse)
async def review_course_plan(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    plan_id: int,
    decision: str = Form(...),
    notes: str = Form(default=""),
):
    repo = MyAdvisorRepository(db)
    service = CoursePlanService(db, repo)
    advisor = repo.ensure_advisor_record(user)
    plan = repo.get_course_plan(plan_id)

    if plan is None or plan.status != "submitted":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submitted course plan not found")

    service.review_course_plan(plan_id=plan.id, decision=decision, notes=notes, advisor_id=advisor.id)
    flash(request, f"Course plan {decision}.", "success")
    return RedirectResponse(url=request.url_for("admin_home_view"), status_code=status.HTTP_303_SEE_OTHER)

