from app.config.db import BaseAlchemyModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, DateTime, TIMESTAMP
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import UserModel


class TeamModel(BaseAlchemyModel):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    invite_code: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=True
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
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
    members: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="team", foreign_keys="UserModel.team_id"
    )
    creator: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[created_by])

    def __str__(self):
        return self.name
