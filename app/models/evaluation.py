from app.config.db import BaseAlchemyModel
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, Text, DateTime, ForeignKey
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import UserModel, TaskModel


class EvaluationModel(BaseAlchemyModel):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=True)
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
    employee: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[employee_id], back_populates="evaluations"
    )
    reviewer: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[reviewer_id], back_populates="given_evaluations"
    )
    task: Mapped["TaskModel"] = relationship("TaskModel", back_populates="evaluations")
