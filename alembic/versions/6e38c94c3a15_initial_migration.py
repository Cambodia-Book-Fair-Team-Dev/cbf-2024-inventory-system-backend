"""Initial migration

Revision ID: 6e38c94c3a15
Revises: 
Create Date: 2024-12-07 23:54:44.344747

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6e38c94c3a15'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transaction')
    op.drop_table('category')
    op.drop_table('volunteer')
    op.drop_table('item')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('code', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('item_name', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('qty', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('unit', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('category', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('code', name='item_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('volunteer',
    sa.Column('id', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('kh_name', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    sa.Column('kh_team', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('team', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='volunteer_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('category',
    sa.Column('id', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='category_pkey')
    )
    op.create_table('transaction',
    sa.Column('transaction_id', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('volunteer_id', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('item_code', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('borrow_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('return_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('qty_borrowed', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['item_code'], ['item.code'], name='transaction_item_code_fkey'),
    sa.ForeignKeyConstraint(['volunteer_id'], ['volunteer.id'], name='transaction_volunteer_id_fkey'),
    sa.PrimaryKeyConstraint('transaction_id', name='transaction_pkey')
    )
    # ### end Alembic commands ###
