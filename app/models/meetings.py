from datetime import UTC, datetime
from app.config.db import BaseAlchemyModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Table, Text, DateTime, ForeignKey, Column
from typing import TYPE_CHECKING

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


class MeetingModel(BaseAlchemyModel):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    start_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    location: Mapped[str] = mapped_column(String(255))
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), nullable=False
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
    creator: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[created_by])
    team: Mapped["TeamModel"] = relationship("TeamModel")
    participants: Mapped["UserModel"] = relationship(
        "UserModel", secondary=meeting_participants, back_populates="meetings"
    )

    def __str__(self):
        return self.title
