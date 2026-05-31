"""Add file_path column to documents for persistent PDF storage.

Revision ID: 0006_doc_file_path
Revises: 0005_notes_resolution
Create Date: 2026-05-31 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_doc_file_path"
down_revision = "0005_notes_resolution"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_path VARCHAR(500)"
    )


def downgrade() -> None:
    op.drop_column("documents", "file_path")
