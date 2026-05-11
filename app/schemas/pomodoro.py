from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.pomodoro import PomodoroType


class PomodoroSessionCreate(BaseModel):
    task_id: int | None = None
    session_type: PomodoroType = PomodoroType.WORK
    duration_minutes: int = Field(default=25, ge=1, le=180)
    completed: bool = True


class PomodoroSessionRead(BaseModel):
    id: int
    user_id: int
    task_id: int | None
    session_type: PomodoroType
    duration_minutes: int
    started_at: datetime
    ended_at: datetime | None
    completed: bool

    model_config = ConfigDict(from_attributes=True)
