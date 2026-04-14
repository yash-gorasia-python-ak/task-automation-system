from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.schemas.task_schema import TaskStatus, TaskType
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user_model import User

class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    task_type: Mapped[TaskType] = mapped_column(default=TaskType.SEND_COMIC)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.PENDING)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"), nullable=False, index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="tasks")
