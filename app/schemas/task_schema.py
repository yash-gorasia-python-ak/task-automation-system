from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class TaskType(str, Enum):
    REMINDER = "reminder"
    SYSTEM_CHECK = "system_check"
    SEND_COMIC = "send_comic"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskCreate(BaseModel):
    name: str
    task_type: TaskType
    description: Optional[str | None]
    interval_time: Optional[int | None]
    schedule_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
