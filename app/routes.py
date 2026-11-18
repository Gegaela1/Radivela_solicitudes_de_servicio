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


from typing import Literal


class StaffRegistration(Registration):
    roles: set[Literal["atencion", "coordinacion", "solicitante"]]


@api.post("/personal", status_code=201)
def register_staff(data: StaffRegistration, db: DB, actor: Actor):
    require(actor, "coordinacion")
    if not data.roles.intersection({"atencion", "coordinacion"}):
        raise HTTPException(422, "Seleccione al menos un rol interno")
    return create_user(db, data, sorted(data.roles))


@api.get("/personal")
def staff(db: DB, actor: Actor):
    require(actor, "coordinacion")
    return [{"id": user.id, "nombre": user.nombre} for user in db.scalars(
        select(User).where(User.activo.is_(True)).order_by(User.nombre, User.id)
    ) if "atencion" in user.roles]


from uuid import uuid4

from pydantic import Field
from sqlalchemy import DateTime, ForeignKey, Integer, func, update


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Service(Base):
    __tablename__ = "servicio"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String, unique=True)
    disponible: Mapped[bool] = mapped_column(default=True)
    prioridad: Mapped[str] = mapped_column(String, default="Normal")
    dias: Mapped[int] = mapped_column(default=7)


class Case(Base):
    __tablename__ = "solicitud"
    id: Mapped[int] = mapped_column(primary_key=True)
    radicado: Mapped[str] = mapped_column(String, unique=True)
    titular: Mapped[int] = mapped_column(ForeignKey("usuario.id"), index=True)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicio.id"))
    nombre: Mapped[str] = mapped_column(String)
    documento: Mapped[str] = mapped_column(String)
    correo: Mapped[str] = mapped_column(String)
    asunto: Mapped[str] = mapped_column(String)
    descripcion: Mapped[str] = mapped_column(String)
    estado: Mapped[str] = mapped_column(String, default="Recibida")
    creada: Mapped[datetime] = mapped_column(DateTime, default=now)
    cerrada: Mapped[datetime | None] = mapped_column(DateTime)
    gestor: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    responsable: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    principal: Mapped[int | None] = mapped_column(ForeignKey("solicitud.id"))
    version: Mapped[int] = mapped_column(default=1)
    prioridad: Mapped[str] = mapped_column(String)
    dias: Mapped[int] = mapped_column(Integer)


class Event(Base):
    __tablename__ = "evento"
    id: Mapped[int] = mapped_column(primary_key=True)
    caso: Mapped[int] = mapped_column(ForeignKey("solicitud.id"), index=True)
    autor: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    tipo: Mapped[str] = mapped_column(String)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=now)
    motivo: Mapped[str | None] = mapped_column(String)
    visible: Mapped[bool] = mapped_column(default=True)


class Submission(Input):
    nombre: Name
    documento: Code
    correo: EmailStr
    servicio_id: int = Field(gt=0)
    asunto: Name
    descripcion: Message


def catalog_item(db, service_id, allow_other=True):
    item = db.get(Service, service_id)
    if not item or not item.disponible or (not allow_other and item.nombre == "Otro servicio"):
        raise HTTPException(422, "Seleccione un servicio disponible")
    return item


def event(db, case, actor, kind, reason=None, visible=True):
    item = Event(caso=case.id, autor=actor.id, tipo=kind, motivo=reason, visible=visible)
    db.add(item)
    return item


def stamp(value):
    return value.replace(tzinfo=timezone.utc).isoformat() if value else None


def summary(case):
    return {**{key: getattr(case, key) for key in (
        "radicado", "servicio_id", "asunto", "estado", "version", "gestor",
        "responsable", "prioridad", "dias",
    )}, "creada": stamp(case.creada), "cerrada": stamp(case.cerrada)}


@api.post("/solicitudes", status_code=201)
def submit(data: Submission, db: DB, actor: Actor):
    require(actor, "solicitante")
    item = catalog_item(db, data.servicio_id)
    case = Case(**data.model_dump(), titular=actor.id, prioridad=item.prioridad, dias=item.dias,
                radicado=f"RAD-{now().year}-{uuid4().hex[:16].upper()}")
    db.add(case)
    db.flush()
    event(db, case, actor, "Radicación")
    db.commit()
    return summary(case)


@api.get("/servicios")
def services(db: DB, actor: Actor):
    return [{"id": item.id, "nombre": item.nombre, "prioridad": item.prioridad, "dias": item.dias}
            for item in db.scalars(select(Service).where(Service.disponible).order_by(Service.id))]


def find_case(db, radicado):
    case = db.scalar(select(Case).where(Case.radicado == radicado.strip().upper()))
    if not case:
        raise HTTPException(404, "Solicitud no encontrada")
    return case


def allowed_case(db, actor, radicado):
    case = find_case(db, radicado)
    if (case.titular == actor.id or "coordinacion" in actor.roles
            or ("atencion" in actor.roles and (
                actor.id in (case.gestor, case.responsable) or case.estado == "Recibida"
            ))):
        return case
    raise HTTPException(404, "Solicitud no encontrada")


def detail(db, case, actor):
    result = {**summary(case), **{key: getattr(case, key) for key in (
        "nombre", "documento", "correo", "descripcion",
    )}}
    result["acciones"] = actions(db, case, actor)
    return result


def actions(db, case, actor):
    return [name for name, condition in action_rules(db, case, actor).items() if condition]


def action_rules(db, case, actor):
    return {}


@api.get("/solicitudes")
def own_cases(db: DB, actor: Actor, offset: int = 0, limite: int = 50):
    if offset < 0 or not 1 <= limite <= 100:
        raise HTTPException(422, "Paginación inválida")
    return [summary(case) for case in db.scalars(
        select(Case).where(Case.titular == actor.id).order_by(Case.id.desc())
        .offset(offset).limit(limite)
    )]


@api.get("/solicitudes/{radicado}")
def get_case(radicado: str, db: DB, actor: Actor):
    return detail(db, allowed_case(db, actor, radicado), actor)


class Version(Input):
    version: int = Field(gt=0)


class Correction(Version):
    nombre: Name | None = None
    documento: Code | None = None
    correo: EmailStr | None = None
    servicio_id: int | None = Field(default=None, gt=0)
    asunto: Name | None = None
    descripcion: Message | None = None


def owned_case(db, radicado, actor):
    require(actor, "solicitante")
    case = find_case(db, radicado)
    if case.titular != actor.id:
        raise HTTPException(404, "Solicitud no encontrada")
    return case


def transition(db, case, version, expected, values):
    states = [expected] if isinstance(expected, str) else expected
    result = db.execute(update(Case).where(
        Case.id == case.id, Case.version == version, Case.estado.in_(states)
    ).values(**values, version=Case.version + 1))
    if result.rowcount != 1:
        raise HTTPException(409, "La solicitud cambió o su estado impide la operación")


@api.patch("/solicitudes/{radicado}")
def correct(radicado: str, data: Correction, db: DB, actor: Actor):
    case = owned_case(db, radicado, actor)
    changes = data.model_dump(exclude_unset=True, exclude={"version"})
    if not changes or None in changes.values():
        raise HTTPException(422, "Indique campos válidos para corregir")
    if "servicio_id" in changes:
        item = catalog_item(db, changes["servicio_id"])
        if item.id != case.servicio_id:
            changes.update(prioridad=item.prioridad, dias=item.dias)
    transition(db, case, data.version, "Recibida", changes)
    event(db, case, actor, "Corrección", ", ".join(
        key for key in changes if key not in {"prioridad", "dias"}
    ))
    db.commit()
    return detail(db, case, actor)


@api.post("/solicitudes/{radicado}/cancelar")
def cancel(radicado: str, data: Version, db: DB, actor: Actor):
    case = owned_case(db, radicado, actor)
    transition(db, case, data.version, "Recibida", {"estado": "Cancelada", "cerrada": now()})
    event(db, case, actor, "Cancelación")
    db.commit()
    return detail(db, case, actor)

