from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"


def upgrade():
    services = op.create_table(
        "servicio",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nombre", sa.String, nullable=False, unique=True),
        sa.Column("disponible", sa.Boolean, nullable=False),
        sa.Column("prioridad", sa.String, nullable=False),
        sa.Column("dias", sa.Integer, nullable=False),
    )
    op.bulk_insert(services, [
        dict(nombre=name, dias=days, disponible=True, prioridad="Normal")
        for name, days in [
            ("Consulta sobre trámites", 2), ("Actualización de información", 3),
            ("Solicitud de documentos", 5), ("Expedición de certificados", 5),
            ("Petición general", 7), ("Otro servicio", 7),
        ]
    ])
    op.create_table(
        "solicitud",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("radicado", sa.String, unique=True, nullable=False),
        sa.Column("titular", sa.Integer, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("servicio_id", sa.Integer, sa.ForeignKey("servicio.id"), nullable=False),
        *(sa.Column(name, sa.String, nullable=False) for name in (
            "nombre", "documento", "correo", "asunto", "descripcion", "estado", "prioridad"
        )),
        sa.Column("creada", sa.DateTime, nullable=False),
        sa.Column("cerrada", sa.DateTime),
        sa.Column("gestor", sa.Integer, sa.ForeignKey("usuario.id")),
        sa.Column("responsable", sa.Integer, sa.ForeignKey("usuario.id")),
        sa.Column("principal", sa.Integer, sa.ForeignKey("solicitud.id")),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("dias", sa.Integer, nullable=False),
    )
    op.create_index("ix_solicitud_titular", "solicitud", ["titular"])
    op.create_table(
        "evento",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("caso", sa.Integer, sa.ForeignKey("solicitud.id"), nullable=False),
        sa.Column("autor", sa.Integer, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("tipo", sa.String, nullable=False),
        sa.Column("fecha", sa.DateTime, nullable=False),
        sa.Column("motivo", sa.String),
        sa.Column("visible", sa.Boolean, nullable=False),
    )
    op.create_index("ix_evento_caso", "evento", ["caso"])


def downgrade():
    op.drop_table("evento")
    op.drop_table("solicitud")
    op.drop_table("servicio")
