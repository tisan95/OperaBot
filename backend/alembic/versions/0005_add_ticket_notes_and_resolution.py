"""Add ticket_notes table and resolution_message to tickets.

Revision ID: 0005_add_ticket_notes_and_resolution
Revises: 0004_add_super_admin_role
Create Date: 2026-05-31 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_notes_resolution"
down_revision = "0004_add_super_admin_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add resolution_message — IF NOT EXISTS handles the case where
    # init_db() already created it via create_all()
    op.execute(
        "ALTER TABLE tickets ADD COLUMN IF NOT EXISTS resolution_message TEXT"
    )

    # Create ticket_notes — may already exist if init_db() ran first
    op.execute("""
        CREATE TABLE IF NOT EXISTS ticket_notes (
            id SERIAL PRIMARY KEY,
            ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
            author_id UUID NOT NULL REFERENCES users(id),
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_ticket_notes_ticket_id ON ticket_notes (ticket_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_ticket_notes_ticket_id")
    op.drop_table("ticket_notes")
    op.drop_column("tickets", "resolution_message")
