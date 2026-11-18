from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"


def upgrade():
    op.create_table(
        "requerimiento",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("caso", sa.Integer, sa.ForeignKey("solicitud.id"), nullable=False),
        sa.Column("tipo", sa.String, nullable=False),
        sa.Column("detalle", sa.String, nullable=False),
        sa.Column("abierta", sa.Boolean, nullable=False),
        sa.Column("respuesta", sa.String),
        sa.Column("inicio", sa.DateTime, nullable=False),
        sa.Column("fin", sa.DateTime),
    )
    op.create_index("ix_requerimiento_caso", "requerimiento", ["caso"])
    op.create_index("uq_requerimiento_abierto", "requerimiento", ["caso"],
                    unique=True, sqlite_where=sa.text("abierta = 1"))


def downgrade():
    op.drop_table("requerimiento")
