"""add meeting status

Revision ID: 2909cb57fd67
Revises: 962d8aa60835
Create Date: 2026-07-20 04:28:03.717840

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "2909cb57fd67"
down_revision: Union[str, Sequence[str], None] = "962d8aa60835"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Создаём Enum-тип в PostgreSQL
    op.execute(
        "CREATE TYPE meetingstatusemun AS ENUM ('PLANNED', 'CANCELED', 'COMPLETED', 'IN_PROGRESS')"
    )

    # 2. Добавляем колонки
    op.add_column(
        "meetings",
        sa.Column(
            "status",
            sa.Enum(name="meetingstatusemun"),
            nullable=False,
            server_default="PLANNED",
        ),
    )
    op.add_column(
        "meetings", sa.Column("cancellation_reason", sa.Text(), nullable=True)
    )
    op.add_column(
        "meetings", sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "meetings", sa.Column("canceled_by", sa.Integer(), nullable=True)
    )  # исправлено название

    # 3. Обновляем внешние ключи (сначала удаляем старые, затем добавляем с ON DELETE SET NULL)
    op.drop_constraint(op.f("meetings_created_by_fkey"), "meetings", type_="foreignkey")
    op.drop_constraint(op.f("meetings_team_id_fkey"), "meetings", type_="foreignkey")

    op.create_foreign_key(
        None, "meetings", "users", ["created_by"], ["id"], ondelete="SET NULL"
    )
    op.create_foreign_key(
        None, "meetings", "teams", ["team_id"], ["id"], ondelete="SET NULL"
    )
    op.create_foreign_key(
        None, "meetings", "users", ["canceled_by"], ["id"], ondelete="SET NULL"
    )


def downgrade() -> None:
    # 1. Удаляем новые внешние ключи
    op.drop_constraint(None, "meetings", type_="foreignkey")
    op.drop_constraint(None, "meetings", type_="foreignkey")
    op.drop_constraint(None, "meetings", type_="foreignkey")

    # 2. Восстанавливаем старые внешние ключи
    op.create_foreign_key(
        op.f("meetings_created_by_fkey"), "meetings", "users", ["created_by"], ["id"]
    )
    op.create_foreign_key(
        op.f("meetings_team_id_fkey"), "meetings", "teams", ["team_id"], ["id"]
    )

    # 3. Удаляем добавленные колонки
    op.drop_column("meetings", "status")
    op.drop_column("meetings", "cancellation_reason")
    op.drop_column("meetings", "canceled_at")
    op.drop_column("meetings", "canceled_by")

    # 4. Удаляем Enum-тип
    op.execute("DROP TYPE meetingstatusemun")
