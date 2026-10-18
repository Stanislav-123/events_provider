"""add tickets sync_state and indexes

Revision ID: b2c4d6e8f0a1
Revises: ecd13b996e8b
Create Date: 2026-10-18 18:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "b2c4d6e8f0a1"
down_revision: Union[str, Sequence[str], None] = "ecd13b996e8b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sync_state",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("last_sync_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_status", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tickets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("event_id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("seat", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tickets_event_id"),
        "tickets",
        ["event_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_events_event_time"),
        "events",
        ["event_time"],
        unique=False,
    )
    op.create_index(
        op.f("ix_events_changed_at"),
        "events",
        ["changed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_events_changed_at"), table_name="events")
    op.drop_index(op.f("ix_events_event_time"), table_name="events")
    op.drop_index(op.f("ix_tickets_event_id"), table_name="tickets")
    op.drop_table("tickets")
    op.drop_table("sync_state")
