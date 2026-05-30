from app.config.db import BaseAlchemyModel
from enum import StrEnum, Enum
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import TaskModel, TeamModel, EvaluationModel, MeetingModel
from datetime import datetime


class UserRole(StrEnum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class UserModel(BaseAlchemyModel):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True, index=True)
    email = mapped_column(String, unique=True, index=True, nullable=False)
    username = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password = mapped_column(String, nullable=False)
    full_name = mapped_column(String, nullable=True)
    role = mapped_column(Enum(UserRole), default=UserRole.USER)
    is_active = mapped_column(Boolean, default=True)
    team_id = mapped_column(Integer, ForeignKey("teams.id"), nullable=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    team = relationship(TeamModel, back_populates="members")
    created_tasks = relationship(
        TaskModel, foreign_keys="Task.created_by", back_populates="creator"
    )
    assigned_tasks = relationship(
        TaskModel, foreign_keys="Task.assignee_id", back_populates="assignee"
    )
    evaluations = relationship(
        EvaluationModel,
        foreign_keys="Evaluation.employee_id",
        back_populates="employee",
    )
    given_evaluations = relationship(
        EvaluationModel,
        foreign_keys="Evaluation.reviewer_id",
        back_populates="reviewer",
    )
    meetings = relationship(
        MeetingModel, secondary="meeting_participants", back_populates="participants"
    )
