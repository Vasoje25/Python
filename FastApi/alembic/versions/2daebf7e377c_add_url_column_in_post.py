"""add_url_column_in_post

Revision ID: 2daebf7e377c
Revises: f3169d33e9ce
Create Date: 2024-03-25 12:56:40.455932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2daebf7e377c'
down_revision: Union[str, None] = 'f3169d33e9ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('image_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'image_url')
    # ### end Alembic commands ###