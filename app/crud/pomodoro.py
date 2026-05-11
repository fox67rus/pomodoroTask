from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.pomodoro import PomodoroSession
from app.schemas.pomodoro import PomodoroSessionCreate


def create_session(db: Session, user_id: int, session_in: PomodoroSessionCreate) -> PomodoroSession:
    started_at = datetime.now(timezone.utc)
    ended_at = started_at + timedelta(minutes=session_in.duration_minutes) if session_in.completed else None
    session = PomodoroSession(
        user_id=user_id,
        task_id=session_in.task_id,
        session_type=session_in.session_type,
        duration_minutes=session_in.duration_minutes,
        started_at=started_at,
        ended_at=ended_at,
        completed=session_in.completed,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_recent_sessions(db: Session, user_id: int, limit: int = 10) -> Sequence[PomodoroSession]:
    stmt = (
        select(PomodoroSession)
        .where(PomodoroSession.user_id == user_id)
        .order_by(PomodoroSession.started_at.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()


def count_today_completed(db: Session, user_id: int) -> int:
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    count = db.scalar(
        select(func.count())
        .select_from(PomodoroSession)
        .where(
            PomodoroSession.user_id == user_id,
            PomodoroSession.completed.is_(True),
            PomodoroSession.started_at >= today_start,
        )
    )
    return count or 0
