"""Add sources field to chat_messages.

Revision ID: 0001_add_chat_message_sources
Revises: 
Create Date: 2026-05-29 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_add_chat_message_sources"
down_revision = "0000_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chat_messages",
        sa.Column(
            "sources",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )
    op.alter_column("chat_messages", "sources", server_default=None)


def downgrade() -> None:
    op.drop_column("chat_messages", "sources")
