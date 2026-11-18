"""Registra fechas no hábiles del calendario de atención."""
import argparse
from datetime import date

from sqlalchemy.orm import Session

from app.config import engine
from app.routes import Holiday


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fechas", nargs="+", type=date.fromisoformat, metavar="AAAA-MM-DD")
    args = parser.parse_args()
    with Session(engine) as db:
        for day in set(args.fechas):
            if db.get(Holiday, day) is None:
                db.add(Holiday(fecha=day))
        db.commit()
    print("Fechas incorporadas al calendario.")


if __name__ == "__main__":
    main()
