from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"


def upgrade():
    op.create_table(
        "aviso",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("destinatario", sa.Integer, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("evento_id", sa.Integer, sa.ForeignKey("evento.id"), unique=True, nullable=False),
        sa.Column("leido", sa.Boolean, nullable=False),
    )
    op.create_index("ix_aviso_destinatario", "aviso", ["destinatario"])


def downgrade():
    op.drop_table("aviso")
