"""change a summ for order2

Revision ID: bffc5b3aeac0
Revises: 19668ba527a4
Create Date: 2023-01-08 14:41:22.684718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bffc5b3aeac0'
down_revision = '19668ba527a4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('order_duration', sa.DateTime))


def downgrade() -> None:
    pass
