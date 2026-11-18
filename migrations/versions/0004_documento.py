from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"


def upgrade():
    op.create_table(
        "documento",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("caso", sa.Integer, sa.ForeignKey("solicitud.id"), nullable=False),
        sa.Column("requerimiento", sa.Integer, sa.ForeignKey("requerimiento.id"), unique=True),
        sa.Column("nombre", sa.String, nullable=False),
        sa.Column("clave", sa.String, nullable=False, unique=True),
        sa.Column("tamano", sa.Integer, nullable=False),
    )
    op.create_index("ix_documento_caso", "documento", ["caso"])


def downgrade():
    op.drop_table("documento")
