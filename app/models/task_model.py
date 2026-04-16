from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.schemas.task_schema import TaskStatus, TaskType
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user_model import User

class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_task_status_last_run_at", "status", "last_run_at"),
    )

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    task_type: Mapped[TaskType] = mapped_column(default=TaskType.SEND_COMIC)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.PENDING)
    interval_time: Mapped[int] = mapped_column(Integer, nullable=True)
    schedule_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"), nullable=False, index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="tasks")
