"""Prepara cuentas ficticias en una base migrada para la sustentación."""
from argparse import ArgumentParser
from getpass import getpass

from pypdf import PdfWriter
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import engine, storage
from app.routes import Registration, User, create_user, hasher

ACCOUNTS = [
    ("Ana Solís (demo)", "D-01", "ana@example.com", ["solicitante"]),
    ("Darío Vega (demo)", "D-02", "atencion@example.com", ["atencion"]),
    ("Irene Ríos (demo)", "D-03", "coord@example.com", ["coordinacion"]),
]


def prepare(password):
    with Session(engine) as db:
        for name, document, email, roles in ACCOUNTS:
            if db.scalar(select(User).where(User.correo == email)) is None:
                create_user(db, Registration(nombre=name, documento=document,
                                             correo=email, contrasena=password), roles)
    storage.mkdir(parents=True, exist_ok=True)
    sample = storage / "certificado-ficticio.pdf"
    if not sample.exists():
        writer = PdfWriter()
        writer.add_blank_page(width=300, height=450)
        writer.add_metadata({"/Title": "Certificado ficticio para la demostración"})
        with sample.open("xb") as target:
            writer.write(target)
    return sample


def reset_passwords(password):
    if not 10 <= len(password) <= 128:
        raise ValueError("La contraseña debe tener entre 10 y 128 caracteres.")
    with Session(engine) as db:
        users = []
        for name, document, email, roles in ACCOUNTS:
            user = db.scalar(select(User).where(User.correo == email))
            if not user or (user.nombre, user.documento, user.roles) != (name, document, roles):
                raise ValueError(f"No se encontró la cuenta ficticia original {email}.")
            users.append(user)
        for user in users:
            user.hash = hasher.hash(password)
        db.commit()


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--restablecer", action="store_true",
                        help="cambia únicamente las contraseñas de las tres cuentas ficticias")
    args = parser.parse_args()
    password = getpass("Contraseña de las cuentas ficticias (mínimo 10): ")
    if not args.restablecer:
        print("PDF de muestra:", prepare(password))
        return
    if password != getpass("Repite la contraseña nueva: "):
        parser.error("Las contraseñas no coinciden.")
    try:
        reset_passwords(password)
    except ValueError as error:
        parser.error(str(error))
    print("Contraseñas de demostración actualizadas.")


if __name__ == "__main__":
    main()
