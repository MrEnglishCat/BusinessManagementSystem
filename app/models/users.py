from app.config.db import BaseAlchemyModel
from enum import Enum
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Enum as DB_Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import TaskModel, TeamModel, EvaluationModel, MeetingModel


class UserRole(str, Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class UserModel(BaseAlchemyModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(DB_Enum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    team_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("teams.id"), nullable=True
    )
    created_at: Mapped[int] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[int] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
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
