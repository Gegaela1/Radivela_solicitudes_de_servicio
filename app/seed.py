from getpass import getpass

from sqlalchemy.orm import Session

from app.config import engine
from app.routes import Registration, create_user


def main():
    data = Registration(nombre="Coordinación demo", documento="DEMO-001",
                        correo=input("Correo de coordinación: "),
                        contrasena=getpass("Contraseña nueva: "))
    with Session(engine) as db:
        create_user(db, data, ["coordinacion", "atencion"])


if __name__ == "__main__":
    main()
