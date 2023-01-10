"""change a summ for order

Revision ID: 19668ba527a4
Revises: 
Create Date: 2023-01-08 14:02:58.531407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19668ba527a4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('order_duration', sa.Float))


def downgrade() -> None:
    op.drop_column('orders', 'order_duration')
