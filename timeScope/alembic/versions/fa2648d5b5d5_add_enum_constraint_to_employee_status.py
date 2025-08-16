"""Add enum constraint to employee status

Revision ID: fa2648d5b5d5
Revises: 64e3afa8134a
Create Date: 2025-07-07 19:28:22.888036

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa2648d5b5d5'
down_revision = '64e3afa8134a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table("employees", schema=None) as batch_op:
        batch_op.create_check_constraint(
            "ck_employee_status",
            sa.text("status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')")
        )


def downgrade() -> None:
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table("employees", schema=None) as batch_op:
        batch_op.drop_constraint("ck_employee_status", type_="check") 