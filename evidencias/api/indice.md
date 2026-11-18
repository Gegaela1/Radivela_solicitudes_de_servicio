# Evidencias por endpoint

Registré las solicitudes y respuestas de las 26 operaciones de la API en el orden en que se ejecutaron. Cada archivo del índice muestra las entradas, las respuestas y los códigos esperados y observados. Los pasos conservan su numeración global para seguir el flujo entre archivos.

El registro contiene **75 llamadas HTTP aprobadas**. Los archivos muestran el estado de cada comparación HTTP. Las aserciones del flujo y las indicaciones para repetirlo están en [Pruebas de Radivela](../../docs/pruebas.md).

| Método | Endpoint | Pruebas | Códigos observados | Evidencia |
|---|---|---|---|---|
| `GET` | `/api/v1/avisos` | PF-12 | 200 | [Solicitudes y respuestas](01-get-avisos.json) |
| `GET` | `/api/v1/bandeja` | PF-08 | 200 | [Solicitudes y respuestas](02-get-bandeja.json) |
| `GET` | `/api/v1/personal` | PF-10 | 200, 403 | [Solicitudes y respuestas](03-get-personal.json) |
| `GET` | `/api/v1/salud` | OP-01 | 200 | [Solicitudes y respuestas](04-get-salud.json) |
| `GET` | `/api/v1/servicios` | PF-04 | 200, 401 | [Solicitudes y respuestas](05-get-servicios.json) |
| `GET` | `/api/v1/solicitudes` | PF-02, G02 | 200, 401 | [Solicitudes y respuestas](06-get-solicitudes.json) |
| `GET` | `/api/v1/solicitudes/{radicado}` | PF-05, PF-02/PF-05, G04, PF-05/G03, G07, G06, G09, PF-15, PF-17, G11 | 200, 401, 404 | [Solicitudes y respuestas](07-get-solicitudes-radicado.json) |
| `GET` | `/api/v1/solicitudes/{radicado}/documentos/{document_id}` | PF-14, G11 | 200, 404 | [Solicitudes y respuestas](08-get-solicitudes-radicado-documentos-document_id.json) |
| `GET` | `/api/v1/solicitudes/{radicado}/historial` | PF-07, PF-11/G08 | 200 | [Solicitudes y respuestas](09-get-solicitudes-radicado-historial.json) |
| `GET` | `/api/v1/supervision` | PF-18, PF-18/G10, G10 | 200, 403 | [Solicitudes y respuestas](10-get-supervision.json) |
| `PATCH` | `/api/v1/avisos/{notice_id}` | PF-12 | 200, 404 | [Solicitudes y respuestas](11-patch-avisos-notice_id.json) |
| `PATCH` | `/api/v1/reaperturas/{reopening_id}` | PF-15 | 200, 403 | [Solicitudes y respuestas](12-patch-reaperturas-reopening_id.json) |
| `PATCH` | `/api/v1/servicios/{service_id}` | PF-17 | 200, 403 | [Solicitudes y respuestas](13-patch-servicios-service_id.json) |
| `PATCH` | `/api/v1/solicitudes/{radicado}` | PF-06 | 200, 409 | [Solicitudes y respuestas](14-patch-solicitudes-radicado.json) |
| `POST` | `/api/v1/auth/login` | PF-02, PF-03 | 200, 401 | [Solicitudes y respuestas](15-post-auth-login.json) |
| `POST` | `/api/v1/auth/registro` | PF-01 | 201, 409, 422 | [Solicitudes y respuestas](16-post-auth-registro.json) |
| `POST` | `/api/v1/personal` | PF-03 | 201, 403 | [Solicitudes y respuestas](17-post-personal.json) |
| `POST` | `/api/v1/solicitudes` | PF-04/G02, PF-04/G01, PF-07, PF-16, PF-17 | 201, 422 | [Solicitudes y respuestas](18-post-solicitudes.json) |
| `POST` | `/api/v1/solicitudes/{radicado}/asignacion` | PF-10/G06, PF-10 | 200, 403 | [Solicitudes y respuestas](19-post-solicitudes-radicado-asignacion.json) |
| `POST` | `/api/v1/solicitudes/{radicado}/cancelar` | PF-07 | 200, 409 | [Solicitudes y respuestas](20-post-solicitudes-radicado-cancelar.json) |
| `POST` | `/api/v1/solicitudes/{radicado}/complementos` | PF-09 | 200, 415, 422 | [Solicitudes y respuestas](21-post-solicitudes-radicado-complementos.json) |
| `POST` | `/api/v1/solicitudes/{radicado}/duplicado` | PF-16 | 200, 403, 422 | [Solicitudes y respuestas](22-post-solicitudes-radicado-duplicado.json) |
| `POST` | `/api/v1/solicitudes/{radicado}/evaluacion` | PF-08 | 200, 422 | [Solicitudes y respuestas](23-post-solicitudes-radicado-evaluacion.json) |
| `POST` | `/api/v1/solicitudes/{radicado}/finalizacion` | PF-13, PF-14, PF-13/PF-14/G09, PF-15 | 200, 422 | [Solicitudes y respuestas](24-post-solicitudes-radicado-finalizacion.json) |
| `POST` | `/api/v1/solicitudes/{radicado}/reaperturas` | PF-15 | 201, 409 | [Solicitudes y respuestas](25-post-solicitudes-radicado-reaperturas.json) |
| `POST` | `/api/v1/solicitudes/{radicado}/revision` | G06, G05, PF-08/G05 | 200, 403, 409 | [Solicitudes y respuestas](26-post-solicitudes-radicado-revision.json) |
