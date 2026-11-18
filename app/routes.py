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


from fastapi import Query
from sqlalchemy import or_, text


class RequestInfo(Base):
    __tablename__ = "requerimiento"
    id: Mapped[int] = mapped_column(primary_key=True)
    caso: Mapped[int] = mapped_column(ForeignKey("solicitud.id"), index=True)
    tipo: Mapped[str] = mapped_column(String)
    detalle: Mapped[str] = mapped_column(String)
    abierta: Mapped[bool] = mapped_column(default=True)
    respuesta: Mapped[str | None] = mapped_column(String)
    inicio: Mapped[datetime] = mapped_column(DateTime, default=now)
    fin: Mapped[datetime | None] = mapped_column(DateTime)


class Evaluation(Version):
    decision: Literal["aceptar", "rechazar", "requerir"]
    motivo: Message | None = None
    tipo: Literal["texto", "documento"] | None = None
    servicio_id: int | None = Field(default=None, gt=0)


@api.get("/bandeja")
def inbox(db: DB, actor: Actor, estado: str | None = None, servicio_id: int | None = None,
          offset: int = Query(0, ge=0), limite: int = Query(50, ge=1, le=100)):
    require(actor, "atencion", "coordinacion")
    query = select(Case)
    if "coordinacion" not in actor.roles:
        query = query.where(or_(Case.estado == "Recibida", Case.responsable == actor.id,
                               Case.responsable.is_(None) & (Case.gestor == actor.id)))
    if estado:
        query = query.where(Case.estado == estado)
    if servicio_id:
        query = query.where(Case.servicio_id == servicio_id)
    return [summary(case) for case in db.scalars(
        query.order_by(Case.id.desc()).offset(offset).limit(limite)
    )]


@api.post("/solicitudes/{radicado}/revision")
def start_review(radicado: str, data: Version, db: DB, actor: Actor):
    require(actor, "atencion")
    case = allowed_case(db, actor, radicado)
    transition(db, case, data.version, "Recibida",
               {"estado": "En revisión", "gestor": actor.id})
    event(db, case, actor, "Inicio de revisión")
    db.commit()
    return detail(db, case, actor)


@api.post("/solicitudes/{radicado}/evaluacion")
def evaluate(radicado: str, data: Evaluation, db: DB, actor: Actor):
    require(actor, "atencion")
    case = allowed_case(db, actor, radicado)
    if case.estado != "En revisión":
        raise HTTPException(409, "El caso debe estar en revisión")
    if case.gestor != actor.id:
        raise HTTPException(403, "Solo el gestor puede evaluar")
    state = {"aceptar": "Aceptada", "rechazar": "Rechazada",
             "requerir": "En espera de información"}[data.decision]
    changes = {"estado": state}
    if data.decision == "aceptar":
        current = db.get(Service, case.servicio_id)
        service = catalog_item(db, data.servicio_id or current.id, allow_other=False)
        if current.nombre != "Otro servicio" and service.id != current.id:
            raise HTTPException(422, "Solo Otro servicio se reclasifica al aceptar")
        if current.id != service.id:
            changes.update(servicio_id=service.id, prioridad=service.prioridad, dias=service.dias)
    elif not data.motivo or (data.decision == "requerir" and not data.tipo):
        raise HTTPException(422, "Indique el motivo y el tipo de complemento si aplica")
    if data.decision == "rechazar":
        changes["cerrada"] = now()
    transition(db, case, data.version, "En revisión", changes)
    if data.decision == "requerir":
        db.add(RequestInfo(caso=case.id, tipo=data.tipo, detalle=data.motivo))
    event(db, case, actor, state, data.motivo)
    db.commit()
    return detail(db, case, actor)


from io import BytesIO

from fastapi import File, Form, UploadFile
from pypdf import PdfReader


class Document(Base):
    __tablename__ = "documento"
    id: Mapped[int] = mapped_column(primary_key=True)
    caso: Mapped[int] = mapped_column(ForeignKey("solicitud.id"), index=True)
    requerimiento: Mapped[int | None] = mapped_column(ForeignKey("requerimiento.id"), unique=True)
    nombre: Mapped[str] = mapped_column(String)
    clave: Mapped[str] = mapped_column(String, unique=True)
    tamano: Mapped[int] = mapped_column(Integer)


def pdf_bytes(upload):
    limit = 10 * 1024 * 1024
    raw = upload.file.read(limit + 1)
    if len(raw) > limit:
        raise HTTPException(413, "El PDF supera 10 MiB")
    if upload.content_type != "application/pdf" or not raw.startswith(b"%PDF-"):
        raise HTTPException(415, "Adjunte un PDF válido")
    try:
        reader = PdfReader(BytesIO(raw), strict=True)
        if reader.is_encrypted or not len(reader.pages):
            raise ValueError("PDF sin páginas disponibles")
    except Exception as error:
        raise HTTPException(415, "Adjunte un PDF legible") from error
    return raw


def commit_pdf(db, case, raw, name, request_id=None, closure=None):
    from app.config import storage

    if raw is None:
        db.commit()
        return
    storage.mkdir(parents=True, exist_ok=True)
    key = uuid4().hex + ".pdf"
    path = storage / key
    try:
        with path.open("xb") as target:
            target.write(raw)
        values = {"cierre_id": closure.id} if closure is not None else {}
        db.add(Document(caso=case.id, requerimiento=request_id,
                        nombre=name, clave=key, tamano=len(raw), **values))
        db.commit()
    except Exception:
        path.unlink(missing_ok=True)
        raise


def open_request(db, case):
    return db.scalar(select(RequestInfo).where(RequestInfo.caso == case.id, RequestInfo.abierta))


@api.post("/solicitudes/{radicado}/complementos")
def complement(radicado: str, db: DB, actor: Actor,
               version: Annotated[int, Form(gt=0)],
               requerimiento: Annotated[int, Form(gt=0)],
               texto: Annotated[str | None, Form(max_length=10000)] = None,
               pdf: Annotated[UploadFile | None, File()] = None):
    case = owned_case(db, radicado, actor)
    request_info = open_request(db, case)
    if not request_info or request_info.id != requerimiento or case.estado != "En espera de información":
        raise HTTPException(409, "El requerimiento ya no está abierto")
    note = (texto or "").strip()
    if request_info.tipo == "texto" and (not note or pdf):
        raise HTTPException(422, "Responda el requerimiento con texto")
    if request_info.tipo == "documento" and not pdf:
        raise HTTPException(422, "Adjunte el PDF solicitado")
    raw = pdf_bytes(pdf) if pdf else None
    transition(db, case, version, "En espera de información", {"estado": "En revisión"})
    request_info.abierta, request_info.respuesta, request_info.fin = False, note or None, now()
    event(db, case, actor, "Complemento recibido", note or None)
    commit_pdf(db, case, raw, "complemento.pdf", request_id=request_info.id)
    return detail(db, case, actor)


class Assignment(Version):
    responsable: int = Field(gt=0)


def eligible(db, user_id):
    user = db.get(User, user_id) if user_id else None
    return user if user and user.activo and "atencion" in user.roles else None


@api.post("/solicitudes/{radicado}/asignacion")
def assign(radicado: str, data: Assignment, db: DB, actor: Actor):
    require(actor, "coordinacion")
    case = allowed_case(db, actor, radicado)
    user = eligible(db, data.responsable)
    if not user:
        raise HTTPException(422, "El responsable debe estar habilitado para atención")
    transition(db, case, data.version, "Aceptada",
               {"estado": "En atención", "responsable": user.id})
    event(db, case, actor, "Asignación", user.nombre)
    db.commit()
    return detail(db, case, actor)


@api.get("/solicitudes/{radicado}/historial")
def history(radicado: str, db: DB, actor: Actor,
            offset: int = Query(0, ge=0), limite: int = Query(50, ge=1, le=100)):
    case = allowed_case(db, actor, radicado)
    query = select(Event, User.nombre).join(User, Event.autor == User.id).where(Event.caso == case.id)
    if case.titular == actor.id and "coordinacion" not in actor.roles:
        query = query.where(Event.visible)
    return [{"id": entry.id, "tipo": entry.tipo, "fecha": stamp(entry.fecha),
             "motivo": entry.motivo, "autor": author}
            for entry, author in db.execute(
                query.order_by(Event.fecha, Event.id).offset(offset).limit(limite)
            )]


class Notice(Base):
    __tablename__ = "aviso"
    id: Mapped[int] = mapped_column(primary_key=True)
    destinatario: Mapped[int] = mapped_column(ForeignKey("usuario.id"), index=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("evento.id"), unique=True)
    leido: Mapped[bool] = mapped_column(default=False)


def notify(db, case, entry):
    db.flush()
    db.add(Notice(destinatario=case.titular, evento_id=entry.id))


@api.get("/avisos")
def notices(db: DB, actor: Actor, offset: int = Query(0, ge=0),
            limite: int = Query(50, ge=1, le=100)):
    query = select(Notice, Event, Case.radicado).join(Event, Notice.evento_id == Event.id).join(
        Case, Event.caso == Case.id
    ).where(Notice.destinatario == actor.id).order_by(Notice.id.desc()).offset(offset).limit(limite)
    return [{"id": notice.id, "tipo": entry.tipo, "fecha": stamp(entry.fecha),
             "radicado": radicado, "leido": notice.leido}
            for notice, entry, radicado in db.execute(query)]


@api.patch("/avisos/{notice_id}")
def read_notice(notice_id: int, db: DB, actor: Actor):
    entry = db.scalar(select(Notice).where(Notice.id == notice_id,
                                         Notice.destinatario == actor.id))
    if not entry:
        raise HTTPException(404, "Aviso no encontrado")
    entry.leido = True
    db.commit()
    return {"id": entry.id, "leido": entry.leido}


class Closure(Base):
    __tablename__ = "cierre"
    id: Mapped[int] = mapped_column(primary_key=True)
    caso: Mapped[int] = mapped_column(ForeignKey("solicitud.id"), index=True)
    autor: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    fecha: Mapped[datetime] = mapped_column(DateTime, default=now)
    respuesta: Mapped[str] = mapped_column(String)
    resultado: Mapped[str] = mapped_column(String)


@api.post("/solicitudes/{radicado}/finalizacion")
def finish(radicado: str, db: DB, actor: Actor, version: Annotated[int, Form(gt=0)],
           respuesta: Annotated[Message, Form()],
           resultado: Annotated[Literal["resuelto", "expedido", "no_expedido", "no_resuelto"], Form()],
           pdf: Annotated[UploadFile | None, File()] = None):
    require(actor, "atencion")
    case = allowed_case(db, actor, radicado)
    if case.responsable != actor.id:
        raise HTTPException(403, "Solo el responsable puede finalizar")
    service = db.get(Service, case.servicio_id)
    is_certificate = service.nombre == "Expedición de certificados"
    if is_certificate != (resultado in {"expedido", "no_expedido"}):
        raise HTTPException(422, "Seleccione un resultado aplicable al servicio")
    if resultado == "expedido" and not pdf:
        raise HTTPException(422, "Adjunte el certificado en PDF")
    raw = pdf_bytes(pdf) if pdf else None
    closed = now()
    transition(db, case, version, "En atención", {"estado": "Finalizada", "cerrada": closed})
    closure = Closure(caso=case.id, autor=actor.id, fecha=closed, respuesta=respuesta,
                      resultado=resultado)
    db.add(closure)
    notify(db, case, event(db, case, actor, "Finalización", resultado))
    commit_pdf(db, case, raw, "respuesta.pdf", closure=closure)
    return detail(db, case, actor)


from fastapi.responses import FileResponse


@api.get("/solicitudes/{radicado}/documentos/{document_id}")
def download(radicado: str, document_id: int, db: DB, actor: Actor):
    from app.config import storage

    case = allowed_case(db, actor, radicado)
    entry = db.scalar(select(Document).where(Document.id == document_id, Document.caso == case.id))
    if not entry or not (storage / entry.clave).is_file():
        raise HTTPException(404, "Documento no encontrado")
    return FileResponse(storage / entry.clave, media_type="application/pdf", filename=entry.nombre,
                        headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})

