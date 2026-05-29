"""Add tickets table for incident escalation.

Revision ID: 0002_add_tickets
Revises: 0001_add_chat_message_sources
Create Date: 2026-05-29 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0002_add_tickets"
down_revision = "0001_add_chat_message_sources"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("open", "in_progress", "resolved", name="ticketstatus"),
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "priority",
            sa.Enum("low", "medium", "high", name="ticketpriority"),
            nullable=False,
            server_default="medium",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_tickets_company_id", "tickets", ["company_id"])
    op.create_index("ix_tickets_user_id", "tickets", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_tickets_user_id", table_name="tickets")
    op.drop_index("ix_tickets_company_id", table_name="tickets")
    op.drop_table("tickets")
    sa.Enum(name="ticketstatus").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="ticketpriority").drop(op.get_bind(), checkfirst=False)
