from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user, get_current_user_optional
from app.crud.pomodoro import create_session, list_recent_sessions
from app.crud.tasks import get_task, list_tasks
from app.models.pomodoro import PomodoroType
from app.models.user import User
from app.schemas.pomodoro import PomodoroSessionCreate, PomodoroSessionRead

router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])


def templates(request: Request):
    return request.app.state.templates


def require_html_user(user: User | None) -> User | RedirectResponse:
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    return user


@router.get("", response_class=HTMLResponse)
def pomodoro_page(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_current_user_optional)],
):
    current_user = require_html_user(user)
    if isinstance(current_user, RedirectResponse):
        return current_user
    return templates(request).TemplateResponse(
        request,
        "pomodoro.html",
        {
            "request": request,
            "user": current_user,
            "tasks": list_tasks(db, current_user.id),
            "recent_sessions": list_recent_sessions(db, current_user.id),
            "session_types": PomodoroType,
        },
    )


@router.post("/sessions", response_model=PomodoroSessionRead)
def complete_session(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    task_id: Annotated[int | None, Form()] = None,
    session_type: Annotated[PomodoroType, Form()] = PomodoroType.WORK,
    duration_minutes: Annotated[int, Form()] = 25,
):
    if task_id and not get_task(db, user.id, task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return create_session(
        db,
        user.id,
        PomodoroSessionCreate(
            task_id=task_id,
            session_type=session_type,
            duration_minutes=duration_minutes,
            completed=True,
        ),
    )


@router.post("/sessions/html")
def complete_session_from_form(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    task_id: Annotated[int | None, Form()] = None,
    session_type: Annotated[PomodoroType, Form()] = PomodoroType.WORK,
    duration_minutes: Annotated[int, Form()] = 25,
):
    if task_id and not get_task(db, user.id, task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    create_session(
        db,
        user.id,
        PomodoroSessionCreate(
            task_id=task_id,
            session_type=session_type,
            duration_minutes=duration_minutes,
            completed=True,
        ),
    )
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/api/sessions", response_model=list[PomodoroSessionRead])
def api_list_sessions(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return list_recent_sessions(db, user.id, limit=50)
