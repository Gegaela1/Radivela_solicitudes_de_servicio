from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"


def upgrade():
    op.add_column("cierre", sa.Column("tiempo", sa.JSON))


def downgrade():
    op.drop_column("cierre", "tiempo")
