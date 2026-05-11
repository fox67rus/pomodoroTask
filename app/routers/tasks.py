from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user, get_current_user_optional
from app.crud.tasks import create_task, delete_task, get_task, list_tasks, update_task, update_task_status
from app.models.task import TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.tasks import TaskCreate, TaskRead, TaskUpdate
from app.utils.forms import parse_datetime, parse_tags

router = APIRouter(tags=["tasks"])


def templates(request: Request):
    return request.app.state.templates


def require_html_user(user: User | None) -> User | RedirectResponse:
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    return user


@router.get("/tasks/new", response_class=HTMLResponse)
def new_task_page(
    request: Request,
    user: Annotated[User | None, Depends(get_current_user_optional)],
):
    current_user = require_html_user(user)
    if isinstance(current_user, RedirectResponse):
        return current_user
    return templates(request).TemplateResponse(
        request,
        "tasks/form.html",
        {
            "request": request,
            "user": current_user,
            "task": None,
            "priorities": TaskPriority,
            "statuses": TaskStatus,
        },
    )


@router.post("/tasks")
def create_task_from_form(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    title: Annotated[str, Form()],
    description: Annotated[str | None, Form()] = None,
    status_value: Annotated[TaskStatus, Form(alias="status")] = TaskStatus.TODO,
    priority: Annotated[TaskPriority, Form()] = TaskPriority.MEDIUM,
    deadline: Annotated[str | None, Form()] = None,
    tags: Annotated[str | None, Form()] = None,
):
    create_task(
        db,
        user.id,
        TaskCreate(
            title=title,
            description=description or None,
            status=status_value,
            priority=priority,
            deadline=parse_datetime(deadline),
            tags=parse_tags(tags),
        ),
    )
    return RedirectResponse(url="/kanban", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
def edit_task_page(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_current_user_optional)],
    task_id: int,
):
    current_user = require_html_user(user)
    if isinstance(current_user, RedirectResponse):
        return current_user
    task = get_task(db, current_user.id, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return templates(request).TemplateResponse(
        request,
        "tasks/form.html",
        {
            "request": request,
            "user": current_user,
            "task": task,
            "priorities": TaskPriority,
            "statuses": TaskStatus,
        },
    )


@router.post("/tasks/{task_id}/edit")
def update_task_from_form(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    task_id: int,
    title: Annotated[str, Form()],
    description: Annotated[str | None, Form()] = None,
    status_value: Annotated[TaskStatus, Form(alias="status")] = TaskStatus.TODO,
    priority: Annotated[TaskPriority, Form()] = TaskPriority.MEDIUM,
    deadline: Annotated[str | None, Form()] = None,
    tags: Annotated[str | None, Form()] = None,
):
    task = get_task(db, user.id, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    update_task(
        db,
        task,
        TaskUpdate(
            title=title,
            description=description or None,
            status=status_value,
            priority=priority,
            deadline=parse_datetime(deadline),
            tags=parse_tags(tags),
        ),
    )
    return RedirectResponse(url="/kanban", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/tasks/{task_id}/delete")
def delete_task_from_form(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    task_id: int,
):
    task = get_task(db, user.id, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    delete_task(db, task)
    return RedirectResponse(url="/kanban", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/tasks/{task_id}/status")
def move_task(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    task_id: int,
    status_value: Annotated[TaskStatus, Form(alias="status")],
    position: Annotated[int | None, Form()] = None,
):
    task = get_task(db, user.id, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    update_task_status(db, task, status_value, position)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/api/tasks", response_model=list[TaskRead])
def api_list_tasks(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return list_tasks(db, user.id)


@router.post("/api/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def api_create_task(
    task_in: TaskCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return create_task(db, user.id, task_in)


@router.get("/api/tasks/{task_id}", response_model=TaskRead)
def api_get_task(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    task_id: int,
):
    task = get_task(db, user.id, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.patch("/api/tasks/{task_id}", response_model=TaskRead)
def api_update_task(
    task_in: TaskUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    task_id: int,
):
    task = get_task(db, user.id, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return update_task(db, task, task_in)


@router.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_task(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    task_id: int,
):
    task = get_task(db, user.id, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    delete_task(db, task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
