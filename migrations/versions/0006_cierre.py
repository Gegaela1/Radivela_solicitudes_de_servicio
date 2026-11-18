from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"


def upgrade():
    op.create_table(
        "cierre",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("caso", sa.Integer, sa.ForeignKey("solicitud.id"), nullable=False),
        sa.Column("autor", sa.Integer, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("fecha", sa.DateTime, nullable=False),
        sa.Column("respuesta", sa.String, nullable=False),
        sa.Column("resultado", sa.String, nullable=False),
    )
    op.create_index("ix_cierre_caso", "cierre", ["caso"])
    with op.batch_alter_table("documento") as batch:
        batch.add_column(sa.Column("cierre_id", sa.Integer))
        batch.create_foreign_key("fk_documento_cierre", "cierre", ["cierre_id"], ["id"])


def downgrade():
    with op.batch_alter_table("documento") as batch:
        batch.drop_constraint("fk_documento_cierre", type_="foreignkey")
        batch.drop_column("cierre_id")
    op.drop_table("cierre")
