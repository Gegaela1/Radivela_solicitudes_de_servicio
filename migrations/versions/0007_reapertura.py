from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"


def upgrade():
    op.create_table("festivo", sa.Column("fecha", sa.Date, primary_key=True))
    op.create_table(
        "reapertura",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("caso", sa.Integer, sa.ForeignKey("solicitud.id"), nullable=False),
        sa.Column("cierre_id", sa.Integer, sa.ForeignKey("cierre.id"), nullable=False),
        sa.Column("motivo", sa.String, nullable=False),
        sa.Column("fecha", sa.DateTime, nullable=False),
        sa.Column("decision", sa.String),
        sa.Column("motivo_decision", sa.String),
        sa.Column("decisor", sa.Integer, sa.ForeignKey("usuario.id")),
        sa.Column("resuelta", sa.DateTime),
    )
    op.create_index("ix_reapertura_caso", "reapertura", ["caso"])
    op.create_index("uq_reapertura_pendiente", "reapertura", ["caso"], unique=True,
                    sqlite_where=sa.text("decision IS NULL"))


def downgrade():
    op.drop_table("reapertura")
    op.drop_table("festivo")
