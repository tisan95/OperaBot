"""Add archived_at to tickets and ticket_retention_days to companies.

The 0003_ticket_archive branch was an orphaned migration never merged into
the main chain (0002 → 0003_add_user_status → ... → 0006). This migration
re-applies those changes idempotently at the correct position in the trunk.

Revision ID: 0007_ticket_archive
Revises: 0006_doc_file_path
Create Date: 2026-09-25
"""

from alembic import op
import sqlalchemy as sa

revision = "0007_ticket_archive"
down_revision = "0006_doc_file_path"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # IF NOT EXISTS handles dev envs where ticket_retention_days was applied manually.
    op.execute(
        "ALTER TABLE companies "
        "ADD COLUMN IF NOT EXISTS ticket_retention_days INTEGER NOT NULL DEFAULT 7"
    )
    op.execute(
        "ALTER TABLE tickets "
        "ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP WITHOUT TIME ZONE"
    )


def downgrade() -> None:
    op.drop_column("tickets", "archived_at")
    op.drop_column("companies", "ticket_retention_days")
