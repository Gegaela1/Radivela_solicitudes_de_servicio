# Radivela

Radivela centraliza solicitudes de servicio desde la radicación hasta la respuesta. El solicitante consulta el caso por su radicado, el personal registra la atención y coordinación asigna casos y consulta tiempos.

- [Requisitos y reglas del trámite](docs/requisitos.md)
- [Diseño y contratos REST](docs/diseno.md)
- [Trazabilidad, ramas y PR](docs/trazabilidad.md)
- [Pruebas y evidencias](docs/pruebas.md)
- [Demostración y guion de 20 minutos](docs/demo.md)

## Instalación en Windows PowerShell

Desde PowerShell, entra en la carpeta que contiene este README. Comprueba Python con `py -3.12 --version`. Si el lanzador indica que falta esa versión, ejecuta `py install 3.12` y comprueba la versión de nuevo antes de continuar.

```powershell
py -3.12 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno de Python 3.12.' }
$python = '.\.venv\Scripts\python.exe'
& $python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Falló la instalación de dependencias.' }
if (-not (Test-Path .env)) {
    $secret = & $python -c 'import secrets; print(secrets.token_hex(32))'
    if ($LASTEXITCODE -ne 0 -or -not $secret) { throw 'Falló la generación del secreto.' }
    $config = (Get-Content .env.example -Raw).Replace('RADIVELA_SECRET=', "RADIVELA_SECRET=$secret")
    [IO.File]::WriteAllText((Join-Path $PWD '.env'), $config)
}
& $python -m alembic upgrade head
& $python -m app.seed
& $python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Genera `.env` una vez por instalación. Para inicializar con cuentas ficticias, ejecuta `& $python -m scripts.demo` en lugar de `app.seed`. Conserva el archivo de entorno, la base y los documentos fuera de Git. La aplicación guarda los PDF en el directorio privado indicado por `RADIVELA_STORAGE`.

En el navegador abre `http://127.0.0.1:8000`. La interfaz y la API usan el mismo origen. OpenAPI está en `/docs` y `/openapi.json`.

## API

Las rutas están bajo `/api/v1`. El acceso devuelve un JWT de una hora. Incluye el encabezado `Authorization: Bearer <token>` en las rutas protegidas y la última `version` del caso en cada modificación.

| Operación | Ejemplo | Resultado |
|---|---|---|
| `POST /auth/registro` | `nombre`, `documento`, `correo`, `contrasena` | 201 y cuenta solicitante |
| `POST /auth/login` | `correo` y `contrasena` | 200 y sesión |
| `POST /solicitudes` | Datos de contacto, `servicio_id`, `asunto` y `descripcion` | 201 y radicado |
| `GET /solicitudes/{radicado}` | Radicado propio | 200 y detalle |
| `POST /solicitudes/{radicado}/finalizacion` | Multipart con `version`, `respuesta`, `resultado` y PDF si corresponde | 200 y estado Finalizada |
| `GET /supervision?estado=Recibida&prioridad=Alta` | Coordinación | 200 y métricas filtradas |

La API devuelve 401 para sesión inválida, 403 para falta de permiso funcional, 404 para recursos inexistentes o ajenos, 409 para cambios incompatibles, 413 para PDF superior a 10 MiB, 415 para archivos incompatibles y 422 para entradas inválidas.

## Verificación

```powershell
& $python -m pip install -r requirements-dev.txt
& $python -m pytest -q -s
```

La evidencia funcional vincula cada control a sus llamadas HTTP. El [guion de demostración](docs/demo.md) incluye la prueba automatizada en navegador y las instrucciones para repetir el recorrido en vivo.

## Operación y alcance

SQLite y el almacenamiento local sirven para una instalación inicial. Las metas se cuentan en días hábiles de Colombia. Registra los festivos que aplique la organización con `& $python -m scripts.calendario AAAA-MM-DD AAAA-MM-DD`. La configuración inicial excluye sábados y domingos.

La entrega cubre el portal, la API, las migraciones y la verificación con datos ficticios. El historial de Git registra los cambios por requisito. La matriz enlaza su evidencia y el PR de cada requisito cuando esté disponible. El canal de WhatsApp corresponde a la ampliación opcional RF-19.
