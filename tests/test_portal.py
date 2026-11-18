import json
import os
from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from secrets import token_hex
from starlette.routing import Match
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import jwt
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from sqlalchemy import text
from sqlalchemy.orm import Session


@pytest.fixture(scope="module")
def system():
    target = os.getenv("RADIVELA_PRUEBAS_DIR")
    directory = nullcontext(target) if target else TemporaryDirectory()
    with directory as temp, pytest.MonkeyPatch.context() as patch:
        folder = Path(temp)
        folder.mkdir(parents=True, exist_ok=True)
        database = folder / "radivela.sqlite"
        if database.exists():
            pytest.fail("Selecciona una carpeta sin base de datos para la verificación.")
        patch.setenv("RADIVELA_DB", str(database))
        patch.setenv("RADIVELA_STORAGE", str(folder / "documentos"))
        patch.setenv("RADIVELA_SECRET", token_hex(32))
        if target:
            patch.setenv("RADIVELA_EVIDENCIA_HTTP", str(folder / "operaciones.json"))
        from app.config import engine
        from app.main import app
        from app.routes import Registration, create_user

        command.upgrade(Config("alembic.ini"), "head")
        credentials = {
            "nombre": "Irene Ríos", "documento": "D-03",
            "correo": "coord@example.com", "contrasena": fixture_password(),
        }
        with Session(engine) as db:
            create_user(db, Registration(**credentials), ["coordinacion"])
        with TestClient(app) as client:
            yield client, engine
        engine.dispose()
        if target:
            (folder / "operaciones.json").write_text(
                json.dumps(operations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )


operations = []
generated_password = token_hex(16)
private_keys = {"contrasena", "access_token", "authorization", "hash"}


def fixture_password():
    return os.getenv("RADIVELA_PRUEBAS_CLAVE", generated_password)


def without_secrets(value):
    if isinstance(value, dict):
        return {key: "[reservado]" if key.lower() in private_keys else without_secrets(item)
                for key, item in value.items()}
    if isinstance(value, list):
        return [without_secrets(item) for item in value]
    return value


def operation(client, case_id, method, route, status, headers=None, **kwargs):
    url = "/api/v1" + route
    result = client.request(method, url, headers=headers, **kwargs)
    endpoint = next(
        (candidate.path for candidate in client.app.routes
         if candidate.matches({"type": "http", "path": result.request.url.path,
                               "method": method})[0] == Match.FULL),
        url,
    )
    media = result.headers.get("content-type", "")
    is_pdf = media.startswith("application/pdf")
    body = result.content if is_pdf else result.json()
    if os.getenv("RADIVELA_EVIDENCIA_HTTP"):
        inputs = kwargs.get("json", kwargs.get("data", {}))
        files = {
            name: {"archivo": file[0], "tipo": file[2], "bytes": len(file[1]),
                   "sha256": sha256(file[1]).hexdigest()}
            for name, file in kwargs.get("files", {}).items()
        }
        operations.append({
            "paso": len(operations) + 1, "prueba": case_id, "metodo": method,
            "endpoint": endpoint, "solicitud": url, "autenticada": bool(headers),
            "entrada": without_secrets(inputs), "archivos": files,
            "esperado": status, "obtenido": result.status_code,
            "estado_http": "Aprobada" if result.status_code == status else "Fallida",
            "respuesta": {"tipo": media, "bytes": len(body), "sha256": sha256(body).hexdigest()}
            if is_pdf else without_secrets(body),
        })
    print(f"{case_id} {method} {url} HTTP {result.status_code} (esperado {status})")
    assert result.status_code == status, result.text
    return body


def identity(name):
    display, document = {
        "ana": ("Ana Solís", "D-01"),
        "atencion": ("Darío Vega", "D-02"),
    }.get(name, ("Persona de prueba " + name, "P-" + name))
    return {"nombre": display, "documento": document,
            "correo": name + "@example.com", "contrasena": fixture_password()}


def credentials(name):
    return {key: identity(name)[key] for key in ("correo", "contrasena")}


def token(client, name, test):
    result = operation(client, test, "POST", "/auth/login", 200, json=credentials(name))
    return {"Authorization": "Bearer " + result["access_token"]}


def submission(service=1):
    return {"nombre": "Ana de prueba", "documento": "DEMO-13", "correo": "ana@example.com",
            "servicio_id": service, "asunto": "Solicitud de orientación administrativa",
            "descripcion": "Requiero información para completar mi trámite."}


def pdf_fixture():
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=450)
    stream = BytesIO()
    writer.write(stream)
    return stream.getvalue()


def test_recorrido(system):
    client, engine = system
    call = lambda *args, **kwargs: operation(client, *args, **kwargs)
    assert call("OP-01", "GET", "/salud", 200)["estado"] == "disponible"
    ana = call("PF-01", "POST", "/auth/registro", 201, json=identity("ana"))
    assert ana["roles"] == ["solicitante"]
    call("PF-01", "POST", "/auth/registro", 409,
         json={**identity("ana"), "correo": "ANA@example.com"})
    call("PF-01", "POST", "/auth/registro", 422,
         json={**identity("otra"), "roles": ["coordinacion"]})
    call("PF-01", "POST", "/auth/registro", 201, json=identity("bea"))
    owner, other, coord = [token(client, name, "PF-02") for name in ("ana", "bea", "coord")]
    call("PF-02", "POST", "/auth/login", 401, json={**credentials("ana"), "contrasena": "errónea"})
    expired = jwt.encode({"sub": str(ana["id"]), "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
                         os.environ["RADIVELA_SECRET"], algorithm="HS256")
    call("PF-02", "GET", "/solicitudes", 401, {"Authorization": "Bearer " + expired})
    staff_data = {**identity("atencion"), "roles": ["atencion"]}
    call("PF-03", "POST", "/personal", 403, owner, json=staff_data)
    staff_id = call("PF-03", "POST", "/personal", 201, coord, json=staff_data)["id"]
    handler = token(client, "atencion", "PF-03")
    assert staff_id in [entry["id"] for entry in call("PF-10", "GET", "/personal", 200, coord)]
    call("PF-10", "GET", "/personal", 403, owner)
    assert 4 in [entry["id"] for entry in call("PF-04", "GET", "/servicios", 200, owner)]
    call("PF-04", "GET", "/servicios", 401)

    bad = submission()
    del bad["asunto"]
    call("PF-04/G02", "POST", "/solicitudes", 422, owner, json=bad)
    assert call("G02", "GET", "/solicitudes", 200, owner) == []
    case = call("PF-04/G01", "POST", "/solicitudes", 201, owner, json=submission(4))
    assert case["estado"] == "Recibida"
    path = "/solicitudes/" + case["radicado"]
    call("PF-05", "GET", path, 401)
    call("PF-02/PF-05", "GET", path, 404, other)
    call("G04", "GET", "/solicitudes/RAD-INEXISTENTE", 404, owner)
    case = call("PF-05/G03", "GET", path, 200, owner)
    assert case["estado"] == "Recibida" and case["asunto"] == submission()["asunto"]
    case = call("PF-06", "PATCH", path, 200, owner,
                json={"version": case["version"], "asunto": "Certificado de afiliación"})
    cancellation = call("PF-07", "POST", "/solicitudes", 201, owner, json=submission())
    canceled_path = "/solicitudes/" + cancellation["radicado"]
    assert call("PF-07", "POST", canceled_path + "/cancelar", 200, owner,
                json={"version": cancellation["version"]})["estado"] == "Cancelada"
    assert any(entry["tipo"] == "Cancelación" for entry in call(
        "PF-07", "GET", canceled_path + "/historial", 200, owner))

    for role in (coord, handler):
        assert any(item["radicado"] == case["radicado"] for item in call("PF-08", "GET", "/bandeja", 200, role))
    call("G06", "POST", path + "/revision", 403, owner, json={"version": case["version"]})
    call("G05", "POST", path + "/revision", 409, handler, json={"version": 1})
    case = call("PF-08/G05", "POST", path + "/revision", 200, handler, json={"version": case["version"]})
    assert case["estado"] == "En revisión"
    assert call("G07", "GET", path, 200, owner)["estado"] == "En revisión"
    call("PF-06", "PATCH", path, 409, owner, json={"version": case["version"], "asunto": "Tarde"})
    call("PF-07", "POST", path + "/cancelar", 409, owner, json={"version": case["version"]})
    call("PF-08", "POST", path + "/evaluacion", 422, handler,
         json={"version": case["version"], "decision": "rechazar"})
    case = call("PF-08", "POST", path + "/evaluacion", 200, handler, json={
        "version": case["version"], "decision": "requerir", "motivo": "Adjunte soporte", "tipo": "documento",
    })
    assert case["estado"] == "En espera de información"
    form = {"version": str(case["version"]), "requerimiento": str(case["requerimiento"]["id"])}
    call("PF-09", "POST", path + "/complementos", 422, owner, data=form)
    call("PF-09", "POST", path + "/complementos", 415, owner, data=form,
         files={"pdf": ("texto.pdf", b"texto", "application/pdf")})
    pdf = pdf_fixture()
    case = call("PF-09", "POST", path + "/complementos", 200, owner, data=form,
                files={"pdf": ("soporte.pdf", pdf, "application/pdf")})
    assert case["estado"] == "En revisión"
    case = call("PF-08", "POST", path + "/evaluacion", 200, handler,
                json={"version": case["version"], "decision": "aceptar"})
    assert case["estado"] == "Aceptada"
    assign = {"version": case["version"], "responsable": staff_id}
    call("PF-10/G06", "POST", path + "/asignacion", 403, handler, json=assign)
    assert call("G06", "GET", path, 200, owner)["estado"] == "Aceptada"
    case = call("PF-10", "POST", path + "/asignacion", 200, coord, json=assign)
    assert case["estado"] == "En atención"

    history = call("PF-11/G08", "GET", path + "/historial", 200, owner)
    assert [entry["tipo"] for entry in history] == [
        "Radicación", "Corrección", "Inicio de revisión", "En espera de información",
        "Complemento recibido", "Aceptada", "Asignación",
    ]
    assert history == sorted(history, key=lambda item: (item["fecha"], item["id"]))
    notices = call("PF-12", "GET", "/avisos", 200, owner)
    assert {entry["tipo"] for entry in notices} == {"En espera de información", "Aceptada"}
    notice_path = f"/avisos/{notices[0]['id']}"
    call("PF-12", "PATCH", notice_path, 404, other)
    assert call("PF-12", "PATCH", notice_path, 200, owner)["leido"]
    data = {"version": str(case["version"]), "resultado": "expedido", "respuesta": "Certificado de afiliación expedido"}
    call("PF-13", "POST", path + "/finalizacion", 422, handler,
         data={"version": case["version"], "resultado": "expedido"})
    call("PF-14", "POST", path + "/finalizacion", 422, handler, data=data)
    case = call("PF-13/PF-14/G09", "POST", path + "/finalizacion", 200, handler, data=data,
                files={"pdf": ("certificado.pdf", pdf, "application/pdf")})
    assert case["estado"] == "Finalizada"
    case = call("G09", "GET", path, 200, owner)
    assert case["cierres"][0]["respuesta"] == data["respuesta"]
    doc = next(item for item in case["documentos"] if item["cierre_id"])
    doc_path = path + "/documentos/" + str(doc["id"])
    assert call("PF-14", "GET", doc_path, 200, owner) == pdf
    call("PF-14", "GET", doc_path, 404, other)

    entry = call("PF-15", "POST", path + "/reaperturas", 201, owner,
                 json={"version": case["version"], "motivo": "Solicito un ajuste"})
    case = call("PF-15", "GET", path, 200, owner)
    assert case["estado"] == "Finalizada" and case["reapertura"]["id"] == entry["id"]
    call("PF-15", "POST", path + "/reaperturas", 409, owner,
         json={"version": case["version"], "motivo": "Segunda petición pendiente"})
    reopen_path = "/reaperturas/" + str(entry["id"])
    call("PF-15", "PATCH", reopen_path, 403, handler,
         json={"version": case["version"], "decision": "aprobar", "motivo": "Procede"})
    case = call("PF-15", "PATCH", reopen_path, 200, coord,
                json={"version": case["version"], "decision": "aprobar", "motivo": "Procede"})
    assert case["estado"] == "En atención" and len(case["cierres"]) == 1
    case = call("PF-15", "POST", path + "/finalizacion", 200, handler,
                data={**data, "version": case["version"], "resultado": "no_expedido"})
    from app import routes
    with pytest.MonkeyPatch.context() as patch:
        future = routes.now() + timedelta(days=30)
        patch.setattr(routes, "now", lambda: future)
        call("PF-15", "POST", path + "/reaperturas", 409, owner,
             json={"version": case["version"], "motivo": "Fuera del plazo"})

    dup = call("PF-16", "POST", "/solicitudes", 201, owner, json=submission())
    dup_path = "/solicitudes/" + dup["radicado"]
    duplicate = {"version": dup["version"], "motivo": "Mismo trámite", "principal": case["radicado"]}
    call("PF-16", "POST", dup_path + "/duplicado", 403, handler, json=duplicate)
    call("PF-16", "POST", dup_path + "/duplicado", 422, coord, json={**duplicate, "principal": dup["radicado"]})
    assert call("PF-16", "POST", dup_path + "/duplicado", 200, coord, json=duplicate)["principal"] == case["radicado"]

    call("PF-17", "PATCH", "/servicios/1", 403, handler, json={"prioridad": "Alta", "dias": 3})
    call("PF-17", "PATCH", "/servicios/1", 200, coord, json={"prioridad": "Alta", "dias": 3})
    new = call("PF-17", "POST", "/solicitudes", 201, owner, json=submission())
    assert (new["prioridad"], new["dias"]) == ("Alta", 3)
    assert call("PF-17", "GET", dup_path, 200, owner)["dias"] == 2
    query = "/supervision?estado=Recibida&servicio_id=1&prioridad=Alta"
    call("PF-18", "GET", query, 403, owner)
    report = call("PF-18/G10", "GET", query, 200, coord)
    assert report["total"] == report["pendientes"] == 1
    assert report["solicitudes"][0]["radicado"] == new["radicado"]
    assert call("G10", "GET", "/supervision", 200, coord)["total"] == 4

    engine.dispose()
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA foreign_key_check")).all() == []
    from app.main import app
    with TestClient(app) as restarted:
        assert operation(restarted, "G11", "GET", path, 200, owner)["estado"] == "Finalizada"
        assert operation(restarted, "G11", "GET", doc_path, 200, owner) == pdf
        assert restarted.get("/").status_code == 200
        assert restarted.get("/assets/portal.js").status_code == 200

    if os.getenv("RADIVELA_EVIDENCIA_HTTP"):
        observed = {(op["metodo"], op["endpoint"]) for op in operations}
        expected = {(method.upper(), route) for route, methods in app.openapi()["paths"].items()
                    if route.startswith("/api/v1/") for method in methods}
        assert observed == expected


def test_calendario(system):
    from app.routes import timing

    monday = datetime(2026, 11, 23, 14)
    case = SimpleNamespace(creada=monday, cerrada=None, dias=2)
    observed = monday + timedelta(days=1)
    assert timing(case, [], None, set(), observed)["vencimiento"].isoformat() == "2026-11-25"
    interval = SimpleNamespace(inicio=monday, fin=monday + timedelta(days=2))
    assert timing(case, [interval], None, set(), observed + timedelta(days=2))[
        "vencimiento"].isoformat() == "2026-11-27"
    excluded = {(monday + timedelta(days=1)).date()}
    assert timing(case, [], None, excluded, observed)["vencimiento"].isoformat() == "2026-11-26"
    print("PF-17 lunes → miércoles | pausa lunes a miércoles → viernes | festivo martes → jueves")
