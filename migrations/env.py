from alembic import context
from app.config import engine

if context.is_offline_mode():
    context.configure(url=str(engine.url), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    with engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()
