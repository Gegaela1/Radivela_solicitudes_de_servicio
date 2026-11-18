import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session

load_dotenv()

engine = create_engine("sqlite:///" + os.getenv("RADIVELA_DB", "radivela.sqlite"))
storage = Path(os.getenv("RADIVELA_STORAGE", "storage"))


@event.listens_for(engine, "connect")
def configure_sqlite(connection, _record):
    connection.execute("PRAGMA foreign_keys = ON")


class Base(DeclarativeBase):
    pass


def session():
    with Session(engine) as db:
        yield db
