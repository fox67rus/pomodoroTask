from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.schemas.tasks import TaskCreate, TaskUpdate


def list_tasks(db: Session, user_id: int) -> Sequence[Task]:
    stmt = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.status, Task.position, Task.created_at.desc())
    )
    return db.scalars(stmt).all()


def list_tasks_by_status(db: Session, user_id: int, status: TaskStatus) -> Sequence[Task]:
    stmt = (
        select(Task)
        .where(Task.user_id == user_id, Task.status == status)
        .order_by(Task.position, Task.created_at.desc())
    )
    return db.scalars(stmt).all()


def get_task(db: Session, user_id: int, task_id: int) -> Task | None:
    return db.scalar(select(Task).where(Task.id == task_id, Task.user_id == user_id))


def create_task(db: Session, user_id: int, task_in: TaskCreate) -> Task:
    max_position = db.scalar(
        select(func.max(Task.position)).where(Task.user_id == user_id, Task.status == task_in.status)
    )
    task = Task(user_id=user_id, position=(max_position or 0) + 1, **task_in.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: Task, task_in: TaskUpdate) -> Task:
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def update_task_status(db: Session, task: Task, status: TaskStatus, position: int | None = None) -> Task:
    task.status = status
    if position is not None:
        task.position = position
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def dashboard_stats(db: Session, user_id: int) -> dict[str, int]:
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    total_done = db.scalar(
        select(func.count()).select_from(Task).where(Task.user_id == user_id, Task.status == TaskStatus.DONE)
    )
    overdue = db.scalar(
        select(func.count())
        .select_from(Task)
        .where(Task.user_id == user_id, Task.deadline.is_not(None), Task.deadline < today_start)
    )
    return {"done": total_done or 0, "overdue": overdue or 0}
