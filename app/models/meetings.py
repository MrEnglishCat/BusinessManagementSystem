from datetime import UTC, datetime

from fastapi import Request
from jinja2 import Template
from app.config.db import BaseAlchemyModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Integer,
    String,
    Table,
    Text,
    DateTime,
    ForeignKey,
    Column,
    Boolean,
    Enum,
)
from typing import TYPE_CHECKING
from enum import StrEnum

if TYPE_CHECKING:
    from . import TeamModel, UserModel

meeting_participants = Table(
    "meeting_participants",
    BaseAlchemyModel.metadata,
    Column(
        "meeting_id",
        Integer,
        ForeignKey("meetings.id", ondelete="CASCADE"),
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
    ),
)


class MeetingStatusEmun(StrEnum):
    PLANNED = "planned"  # только что создана, указано время
    CANCELED = "canceled"  # отменена
    COMPLETED = "completed"  # завершеная встреча, или прошло время
    IN_PROGRESS = (
        "in_progress"  # когда текущее время между началом и окончанием встречи
    )


class MeetingModel(BaseAlchemyModel):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    start_time: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
    )
    location: Mapped[str] = mapped_column(String(255))
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    team_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="SET NULL")
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
    status: Mapped[StrEnum] = mapped_column(
        Enum(MeetingStatusEmun),
        default=MeetingStatusEmun.PLANNED,
        nullable=False,
    )
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    canceled_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
    )
    canceled_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL")
    )

    # Relationships
    creator: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[created_by],
        passive_deletes=True,
        lazy="selectin",
    )
    team: Mapped["TeamModel"] = relationship(
        "TeamModel",
        back_populates="meetings",
        passive_deletes=True,
        lazy="selectin",
    )
    participants: Mapped[list["UserModel"]] = relationship(
        "UserModel",
        secondary=meeting_participants,
        back_populates="meetings",
        lazy="selectin",
    )

    def __str__(self):
        return self.title

    def __admin_repr__(self, request: Request) -> str:
        return self.title

    def __admin_select2_repr__(self, request: Request) -> str:
        return Template(f"<span>{self.title}</span><br>").render()
