"""Add user status field.

Revision ID: 0003_add_user_status
Revises: 0002_add_tickets
Create Date: 2026-05-30 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0003_add_user_status"
down_revision = "0002_add_tickets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "status",
            sa.Enum("pending", "active", name="userstatus"),
            nullable=False,
            server_default="active",
        ),
    )
    # Existing users should remain active after migration; new users can use the ORM default.
    op.alter_column("users", "status", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "status")
    sa.Enum(name="userstatus").drop(op.get_bind(), checkfirst=False)
