"""Add column for a picture

Revision ID: d28bd1a36b30
Revises: 4bf488ec8455
Create Date: 2023-01-24 20:45:33.899514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd28bd1a36b30'
down_revision = '4bf488ec8455'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('car_model', sa.Column('logo_img_path',sa.String, default=None))
    op.add_column('car_actual', sa.Column('logo_img_path', sa.String, default=None))


def downgrade() -> None:
    op.drop_column('car_model', 'logo_img_path')
    op.drop_column('car_actual', 'logo_img_path')

