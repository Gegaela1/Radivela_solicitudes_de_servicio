"""Prepara cuentas ficticias en una base migrada para la sustentación."""
from getpass import getpass

from pypdf import PdfWriter
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import engine, storage
from app.routes import Registration, User, create_user


def prepare(password):
    accounts = [
        ("Ana Solís (demo)", "D-01", "ana@example.com", ["solicitante"]),
        ("Darío Vega (demo)", "D-02", "atencion@example.com", ["atencion"]),
        ("Irene Ríos (demo)", "D-03", "coord@example.com", ["coordinacion"]),
    ]
    with Session(engine) as db:
        for name, document, email, roles in accounts:
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


if __name__ == "__main__":
    print("PDF de muestra:", prepare(getpass("Contraseña de las cuentas ficticias (mínimo 10): ")))
