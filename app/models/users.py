from app.config.db import BaseAlchemyModel
from enum import StrEnum
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as DB_Enum,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import TaskModel, TeamModel, EvaluationModel, MeetingModel

from fastapi_users.db import SQLAlchemyBaseUserTable


class UserRole(StrEnum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class UserModel(SQLAlchemyBaseUserTable[int], BaseAlchemyModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(254),
        unique=True,
        index=True,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(500))
    role: Mapped[UserRole] = mapped_column(DB_Enum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    team_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="SET NULL")
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, server_default=text("false")
    )
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
    team: Mapped["TeamModel"] = relationship(
        "TeamModel", back_populates="members", foreign_keys=team_id
    )
    created_tasks: Mapped["TaskModel"] = relationship(
        "TaskModel", foreign_keys="TaskModel.created_by", back_populates="creator"
    )
    assigned_tasks: Mapped["TaskModel"] = relationship(
        "TaskModel", foreign_keys="TaskModel.assignee_id", back_populates="assignee"
    )
    evaluations: Mapped["EvaluationModel"] = relationship(
        "EvaluationModel",
        foreign_keys="EvaluationModel.employee_id",
        back_populates="employee",
    )
    given_evaluations: Mapped["EvaluationModel"] = relationship(
        "EvaluationModel",
        foreign_keys="EvaluationModel.reviewer_id",
        back_populates="reviewer",
    )
    meetings: Mapped["MeetingModel"] = relationship(
        "MeetingModel", secondary="meeting_participants", back_populates="participants"
    )

    def __str__(self):
        return self.username
