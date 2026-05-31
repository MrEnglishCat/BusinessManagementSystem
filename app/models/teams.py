from app.config.db import BaseAlchemyModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, DateTime
from datetime import datetime
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
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    members: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="team", foreign_keys="UserModel.team_id"
    )
    creator: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[created_by])
