from typing import Annotated

from argon2 import PasswordHasher
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints
from sqlalchemy import JSON, Boolean, String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.config import Base, session

api = APIRouter(prefix="/api/v1")
DB = Annotated[Session, Depends(session)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=180)]
Code = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]
Message = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10000)]
Password = Annotated[str, StringConstraints(min_length=10, max_length=128)]
hasher = PasswordHasher()


class User(Base):
    __tablename__ = "usuario"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String)
    documento: Mapped[str] = mapped_column(String)
    correo: Mapped[str] = mapped_column(String, unique=True)
    hash: Mapped[str] = mapped_column(String)
    roles: Mapped[list[str]] = mapped_column(JSON)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Registration(Input):
    nombre: Name
    documento: Code
    correo: EmailStr
    contrasena: Password


def create_user(db, data, roles):
    user = User(
        nombre=data.nombre, documento=data.documento, correo=data.correo.lower(),
        hash=hasher.hash(data.contrasena), roles=roles,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as error:
        raise HTTPException(409, "El correo ya está registrado") from error
    return {"id": user.id, "nombre": user.nombre, "roles": user.roles}


@api.post("/auth/registro", status_code=201)
def register(data: Registration, db: DB):
    return create_user(db, data, ["solicitante"])

