"""Add freescout_conversation_id to tickets for FreeScout mailbox sync.

Revision ID: 0009_freescout_integration
Revises: 0008_add_chat_sessions
Create Date: 2026-09-26
"""

from alembic import op

revision = "0009_freescout_integration"
down_revision = "0008_add_chat_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE tickets
        ADD COLUMN IF NOT EXISTS freescout_conversation_id INTEGER
    """)


def downgrade() -> None:
    op.drop_column("tickets", "freescout_conversation_id")
