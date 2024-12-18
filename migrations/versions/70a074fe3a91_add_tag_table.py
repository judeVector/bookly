"""add tag table

Revision ID: 70a074fe3a91
Revises: 8eac188db43c
Create Date: 2024-10-30 00:36:01.896330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '70a074fe3a91'
down_revision: Union[str, None] = '8eac188db43c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tags', sa.Column('book_uid', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'tags', 'books', ['book_uid'], ['uid'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tags', type_='foreignkey')
    op.drop_column('tags', 'book_uid')
    # ### end Alembic commands ###
