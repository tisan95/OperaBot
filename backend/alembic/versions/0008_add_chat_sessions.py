"""Add chat_sessions table and session_id FK on chat_messages.

Data migration: existing messages are grouped by (user_id, company_id) and
assigned to a legacy "Historial anterior" session so no history is lost.

Revision ID: 0008_add_chat_sessions
Revises: 0007_ticket_archive
Create Date: 2026-09-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008_add_chat_sessions"
down_revision = "0007_ticket_archive"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create chat_sessions table (IF NOT EXISTS: init_db may have already created it)
    op.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id         SERIAL PRIMARY KEY,
            user_id    UUID NOT NULL REFERENCES users(id),
            company_id UUID NOT NULL REFERENCES companies(id),
            title      VARCHAR(100),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            archived_at TIMESTAMP
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_chat_sessions_user_id    ON chat_sessions (user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_chat_sessions_company_id ON chat_sessions (company_id)")

    # 2. Add nullable session_id FK to chat_messages
    op.execute("""
        ALTER TABLE chat_messages
        ADD COLUMN IF NOT EXISTS session_id INTEGER REFERENCES chat_sessions(id)
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_chat_messages_session_id ON chat_messages (session_id)")

    # 3. Data migration: one "Historial anterior" session per (user_id, company_id) pair
    op.execute("""
        INSERT INTO chat_sessions (user_id, company_id, title, created_at, updated_at)
        SELECT user_id, company_id, 'Historial anterior', MIN(created_at), MAX(created_at)
        FROM chat_messages
        WHERE session_id IS NULL
        GROUP BY user_id, company_id
    """)

    # 4. Assign existing messages to their migration session
    op.execute("""
        UPDATE chat_messages AS m
        SET session_id = s.id
        FROM chat_sessions AS s
        WHERE m.user_id    = s.user_id
          AND m.company_id = s.company_id
          AND m.session_id IS NULL
          AND s.title      = 'Historial anterior'
    """)


def downgrade() -> None:
    op.drop_index("ix_chat_messages_session_id", table_name="chat_messages")
    op.drop_column("chat_messages", "session_id")
    op.drop_index("ix_chat_sessions_company_id", table_name="chat_sessions")
    op.drop_index("ix_chat_sessions_user_id",    table_name="chat_sessions")
    op.drop_table("chat_sessions")
