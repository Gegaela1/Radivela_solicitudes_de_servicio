from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None


def upgrade():
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nombre", sa.String, nullable=False),
        sa.Column("documento", sa.String, nullable=False),
        sa.Column("correo", sa.String, nullable=False, unique=True),
        sa.Column("hash", sa.String, nullable=False),
        sa.Column("roles", sa.JSON, nullable=False),
        sa.Column("activo", sa.Boolean, nullable=False),
    )


def downgrade():
    op.drop_table("usuario")
