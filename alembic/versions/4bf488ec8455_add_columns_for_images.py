"""Add columns for images

Revision ID: 4bf488ec8455
Revises: bffc5b3aeac0
Create Date: 2023-01-23 00:11:04.751255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4bf488ec8455'
down_revision = 'bffc5b3aeac0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('car_company', sa.Column('logo_img_path',sa.String, default=None))


def downgrade() -> None:
    op.drop_column('car_company', 'logo_img_path')
