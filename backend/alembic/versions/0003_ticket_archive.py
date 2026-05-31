"""Add ticket archiving: archived_at on tickets, ticket_retention_days on companies.

Revision ID: 0003_ticket_archive
Revises: 0002_add_tickets
Create Date: 2026-05-31
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_ticket_archive"
down_revision = "0002_add_tickets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tickets", sa.Column("archived_at", sa.DateTime(), nullable=True))
    op.add_column(
        "companies",
        sa.Column("ticket_retention_days", sa.Integer(), nullable=False, server_default="7"),
    )


def downgrade() -> None:
    op.drop_column("tickets", "archived_at")
    op.drop_column("companies", "ticket_retention_days")
