"""Conserva en SQLite los casos de la verificación funcional."""
from argparse import ArgumentParser
from getpass import getpass
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--carpeta", default="storage/verificacion",
                        help="carpeta local para la base y los documentos de la prueba")
    parser.add_argument("--servir", action="store_true", help="abre una verificación ya ejecutada")
    parser.add_argument("--restablecer", action="store_true", help="elige una clave nueva al abrir la base de pruebas")
    parser.add_argument("--puerto", type=int, default=8001)
    args = parser.parse_args()
    folder = Path(args.carpeta).resolve()
    database = folder / "radivela.sqlite"
    env = {
        **os.environ,
        "RADIVELA_DB": str(database),
        "RADIVELA_STORAGE": str(folder / "documentos"),
    }
    if args.servir:
        if not database.is_file():
            parser.error("Ejecuta primero la verificación para generar la base.")
        if args.restablecer:
            env_password = getpass("Contraseña nueva (10 a 128 caracteres): ")
            if env_password != getpass("Confirma la contraseña nueva: "):
                parser.error("Las contraseñas no coinciden.")
            os.environ.update(env)
            from scripts.demo import reset_passwords
            try:
                reset_passwords(env_password)
            except ValueError as error:
                parser.error(str(error))
        cmd = ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(args.puerto)]
    else:
        if args.restablecer:
            parser.error("Usa --restablecer junto a --servir.")
        if database.exists():
            parser.error("La base ya existe. Usa --servir o elige una carpeta nueva con --carpeta.")
        password = getpass("Contraseña para las cuentas de prueba (10 a 128 caracteres): ")
        if not 10 <= len(password) <= 128:
            parser.error("La contraseña debe tener entre 10 y 128 caracteres.")
        env.update(RADIVELA_PRUEBAS_DIR=str(folder), RADIVELA_PRUEBAS_CLAVE=password)
        cmd = ["-m", "pytest", "-q", "-s", "tests/test_portal.py"]
    return subprocess.call([sys.executable, *cmd], env=env)


if __name__ == "__main__":
    sys.exit(main())
