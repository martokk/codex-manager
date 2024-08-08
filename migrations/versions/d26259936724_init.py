"""init

Revision ID: d26259936724
Revises: d6835423c512
Create Date: 2024-07-18 13:09:14.091564

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy import JSON

# revision identifiers, used by Alembic.
revision = "d26259936724"
down_revision = "d6835423c512"
branch_labels = None
depends_on = None


def upgrade():
    # First, try to drop the column if it exists
    try:
        op.drop_column("article", "tags")
    except Exception:
        pass  # Column doesn't exist, so we can proceed to add it

    # Now add the column
    op.add_column("article", sa.Column("tags", JSON(), nullable=True))


def downgrade():
    op.drop_column("article", "tags")
