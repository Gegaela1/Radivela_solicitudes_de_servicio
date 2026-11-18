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


import os
from datetime import datetime, timedelta, timezone

import jwt
from argon2.exceptions import VerificationError
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)
dummy_hash = hasher.hash("comparación para cuentas inexistentes")


class Login(Input):
    correo: EmailStr
    contrasena: Annotated[str, StringConstraints(max_length=128)]


def secret():
    value = os.getenv("RADIVELA_SECRET", "")
    if len(value.encode()) < 32:
        raise HTTPException(503, "El servicio de acceso requiere configuración")
    return value


def unauthorized():
    return HTTPException(401, "Credenciales inválidas o sesión vencida",
                         headers={"WWW-Authenticate": "Bearer"})


@api.post("/auth/login")
def login(data: Login, db: DB):
    user = db.scalar(select(User).where(User.correo == data.correo.lower()))
    try:
        hasher.verify(user.hash if user else dummy_hash, data.contrasena)
    except VerificationError:
        raise unauthorized() from None
    if not user or not user.activo:
        raise unauthorized()
    now = datetime.now(timezone.utc)
    token = jwt.encode({"sub": str(user.id), "iat": now, "exp": now + timedelta(hours=1)},
                       secret(), algorithm="HS256")
    return {"access_token": token, "token_type": "bearer", "roles": user.roles}


def current_user(db: DB, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    if not credentials:
        raise unauthorized()
    try:
        payload = jwt.decode(credentials.credentials, secret(), algorithms=["HS256"],
                             options={"require": ["sub", "exp"]})
        user = db.get(User, int(payload["sub"]))
    except (jwt.InvalidTokenError, ValueError):
        raise unauthorized() from None
    if not user or not user.activo:
        raise unauthorized()
    return user


Actor = Annotated[User, Depends(current_user)]


def require(user, *roles):
    if not set(roles).intersection(user.roles):
        raise HTTPException(403, "No tiene permiso para esta operación")

