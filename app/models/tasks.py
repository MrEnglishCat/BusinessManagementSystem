from app.config.db import BaseAlchemyModel
from enum import Enum
from sqlalchemy import ForeignKey, Integer, Text, DateTime, String, Enum as DB_Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import UserModel, TaskCommentModel, EvaluationModel, TeamModel


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskModel(BaseAlchemyModel):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        DB_Enum(TaskStatus), default=TaskStatus.OPEN
    )
    deadline: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    assignee_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    creator: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[created_by], back_populates="created_tasks"
    )
    assignee: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[assignee_id], back_populates="assigned_tasks"
    )
    team: Mapped["TeamModel"] = relationship("TeamModel")
    comments: Mapped["TaskCommentModel"] = relationship(
        "TaskCommentModel", back_populates="task"
    )
    evaluations: Mapped["EvaluationModel"] = relationship(
        "EvaluationModel", back_populates="task"
    )


class TaskCommentModel(BaseAlchemyModel):
    __tablename__ = "task_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # Relationships
    task: Mapped["TaskModel"] = relationship("TaskModel", back_populates="comments")
    user: Mapped["UserModel"] = relationship("UserModel")
