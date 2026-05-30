"""Add super_admin value to userrole enum.

Revision ID: 0004_add_super_admin_role
Revises: 0003_add_user_status
Create Date: 2026-05-30 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_add_super_admin_role"
down_revision = "0003_add_user_status"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ALTER TYPE ADD VALUE cannot run inside a transaction on PG < 12.
    # Committing first makes it safe on all supported versions.
    connection = op.get_bind()
    connection.execute(sa.text("COMMIT"))
    connection.execute(sa.text("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'super_admin'"))
    connection.execute(sa.text("BEGIN"))


def downgrade() -> None:
    # PostgreSQL does not support removing enum values without recreating the type.
    pass
