from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user_optional
from app.crud.pomodoro import count_today_completed, list_recent_sessions
from app.crud.tasks import dashboard_stats, list_tasks, list_tasks_by_status
from app.models.task import TaskStatus
from app.models.user import User

router = APIRouter(tags=["dashboard"])


def templates(request: Request):
    return request.app.state.templates


def require_html_user(user: User | None) -> User | RedirectResponse:
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    return user


@router.get("/", response_class=HTMLResponse)
def index(user: Annotated[User | None, Depends(get_current_user_optional)]):
    if user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_current_user_optional)],
):
    current_user = require_html_user(user)
    if isinstance(current_user, RedirectResponse):
        return current_user

    tasks = list_tasks(db, current_user.id)
    stats = dashboard_stats(db, current_user.id)
    pomodoro_today = count_today_completed(db, current_user.id)
    recent_sessions = list_recent_sessions(db, current_user.id, limit=5)
    return templates(request).TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "user": current_user,
            "tasks": tasks,
            "stats": stats,
            "pomodoro_today": pomodoro_today,
            "recent_sessions": recent_sessions,
        },
    )


@router.get("/kanban", response_class=HTMLResponse)
def kanban(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_current_user_optional)],
):
    current_user = require_html_user(user)
    if isinstance(current_user, RedirectResponse):
        return current_user

    columns = {
        TaskStatus.TODO: list_tasks_by_status(db, current_user.id, TaskStatus.TODO),
        TaskStatus.IN_PROGRESS: list_tasks_by_status(db, current_user.id, TaskStatus.IN_PROGRESS),
        TaskStatus.DONE: list_tasks_by_status(db, current_user.id, TaskStatus.DONE),
    }
    return templates(request).TemplateResponse(
        request,
        "kanban.html",
        {"request": request, "user": current_user, "columns": columns, "statuses": TaskStatus},
    )
