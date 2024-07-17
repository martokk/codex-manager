"""init

Revision ID: b10ff0670be4
Revises: 0a16ee974a02
Create Date: 2024-07-17 12:39:45.632887

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel # added


# revision identifiers, used by Alembic.
revision = 'b10ff0670be4'
down_revision = '0a16ee974a02'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customcodex',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('context_length', sa.Integer(), nullable=True),
    sa.Column('year_start', sa.Integer(), nullable=True),
    sa.Column('year_end', sa.Integer(), nullable=True),
    sa.Column('tags', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('customcodexarticle',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('codex_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('article_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('article_type', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('custom_text', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['article.id'], ),
    sa.ForeignKeyConstraint(['codex_id'], ['customcodex.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('review',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('article_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('old_summary', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('new_summary', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('old_brief', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('new_brief', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['article.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.add_column(sa.Column('year_start', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('year_end', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('tags', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        batch_op.add_column(sa.Column('text', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        batch_op.add_column(sa.Column('summary', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        batch_op.add_column(sa.Column('brief', sqlmodel.sql.sqltypes.AutoString(), nullable=True))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.drop_column('brief')
        batch_op.drop_column('summary')
        batch_op.drop_column('text')
        batch_op.drop_column('tags')
        batch_op.drop_column('year_end')
        batch_op.drop_column('year_start')

    op.drop_table('review')
    op.drop_table('customcodexarticle')
    op.drop_table('customcodex')
    # ### end Alembic commands ###
