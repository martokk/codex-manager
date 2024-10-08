"""init

Revision ID: 816d7d05a7c9
Revises: e1e69b38c955
Create Date: 2024-07-18 15:22:51.922010

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel # added


# revision identifiers, used by Alembic.
revision = '816d7d05a7c9'
down_revision = 'e1e69b38c955'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.drop_constraint('fk_article_owner_id_user', type_='foreignkey')
        batch_op.drop_column('owner_id')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_id', sa.VARCHAR(), nullable=False))
        batch_op.create_foreign_key('fk_article_owner_id_user', 'user', ['owner_id'], ['id'])

    # ### end Alembic commands ###
