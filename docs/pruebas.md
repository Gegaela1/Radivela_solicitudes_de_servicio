# Pruebas de Radivela

`python -m pytest -q -s` migra una base SQLite temporal y ejecuta los escenarios HTTP con cuentas ficticias. Dejé las entradas completas, las precondiciones y las aserciones en el código de prueba. Guardé la salida de ejecución en [evidencia HTTP](../evidencias/evidencia-http.txt).

## Evidencia por endpoint y casos guardados

Ejecuté las 26 operaciones HTTP de `/api/v1` con datos ficticios en la aplicación real. Para cada llamada guardé el orden, el identificador de prueba, el método, la ruta, los datos enviados, el código esperado, el observado y la respuesta. Para las descargas registré el tipo, el tamaño y la huella SHA-256 del PDF. Omití contraseñas y tokens. [Índice de evidencias por endpoint](../evidencias/api/indice.md)

Para conservar las solicitudes y abrirlas en el portal, ejecuta estos pasos desde PowerShell en la carpeta `Radivela`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m scripts.verificar
.\.venv\Scripts\python.exe -m scripts.verificar --servir
```

El primer comando de verificación te pide escoger una contraseña. Guarda la base, los PDF y `operaciones.json` en `storage/verificacion/`. Entra en [el portal de verificación](http://127.0.0.1:8001) como `ana@example.com` para consultar solicitudes o como `coord@example.com` para revisar el consolidado. La cuenta `atencion@example.com` abre la bandeja. Usa la clave elegida durante la verificación. Si ya generaste la base y no conoces esa clave, ejecuta `python -m scripts.verificar --servir --restablecer` con el Python de `.venv`.

La base local de trabajo y la base de verificación se guardan por separado. Para repetir la verificación completa sin sobrescribir un conjunto anterior, usa `--carpeta storage/verificacion-nueva` tanto al ejecutar las pruebas como al servir sus resultados. Los radicados se asignan en cada ejecución. Busca los que aparezcan en tu registro local.

En Swagger UI, abre `http://127.0.0.1:8001/docs`, realiza el login y usa **Authorize** para repetir consultas con el perfil correspondiente. Para volver a ejecutar operaciones que cambian de estado, usa una verificación nueva o crea un trámite nuevo. El [guion de navegador](demo.md) reproduce el flujo con tres sesiones.

### Casos conservados en esta ejecución

| Radicado | Estado al terminar | Evidencia que se puede consultar |
|---|---|---|
| `RAD-2026-6E58B319E10E40E6` | Finalizada | Historial de revisión, complemento en PDF, asignación, cierre, reapertura aprobada y cierre posterior. |
| `RAD-2026-CDB6E328565743EC` | Cancelada | Registro de la solicitud y actuación de cancelación. |
| `RAD-2026-6E12C4C3D7154028` | Cerrada por duplicado | Motivo y vínculo al radicado principal. |
| `RAD-2026-E272226F8FB0435F` | Recibida | Solicitud creada con la nueva prioridad y regla de tres días. |
| `RAD-2026-17200AD014394D55` | Finalizada | Flujo del navegador con tres perfiles, respuesta y descarga del certificado. |

La verificación del consolidado G10 encontró cuatro solicitudes antes de ejecutar G12. El caso creado desde el navegador es el quinto registro de esta base. Las operaciones inválidas quedan en el registro HTTP.

## Guía de integración

| ID | Entrada o precondición | Resultado esperado y observado |
|---|---|---|
| G01 | Titular envía los seis datos de un certificado | POST 201, radicado y estado Recibida |
| G02 | Titular envía el formulario sin asunto | POST 422. GET 200 devuelve lista vacía |
| G03 | Titular presenta su radicado real | GET 200, devuelve el asunto registrado |
| G04 | Titular busca `RAD-INEXISTENTE` | GET 404 con error controlado |
| G05 | Gestor inicia revisión con versión actual | POST 200 y En revisión. Una versión vieja recibe 409 |
| G06 | Titular inicia revisión o el gestor intenta asignar | POST 403. El caso queda Aceptada tras la asignación rechazada |
| G07 | Titular consulta tras iniciar revisión | GET 200 y En revisión |
| G08 | Titular consulta siete actuaciones | GET 200 y movimientos ordenados por fecha e ID |
| G09 | Responsable adjunta el certificado y finaliza | POST 200. GET 200 con la respuesta en el detalle |
| G10 | Coordinación combina estado, servicio y prioridad | GET 200. Un resultado filtrado y cuatro en el consolidado |
| G11 | Se reinicia Uvicorn y se consulta la misma base | GET 200 para el caso y el PDF. La verificación de claves foráneas devuelve cero infracciones |
| G12 | Tres sesiones de navegador tramitan el certificado | Radicación 201, cierre sin PDF 422, cierre válido y descarga 200. El caso aparece en supervisión. [Registro HTTP](../evidencias/evidencia-navegador.txt) y [captura del detalle](../evidencias/evidencia-g12.png) y [captura del listado](../evidencias/evidencia-listado.png) |

### Revisión del recorrido antes de publicar

Repetí el recorrido en una base de prueba independiente. Con el radicado `RAD-2026-33F884320DFD41BD` comprobé que el titular pudiera ver el requerimiento, que el cierre sin PDF devolviera 422 y mantuviera el estado **En atención**, y que el caso finalizado apareciera en el consolidado. [Requerimiento](../evidencias/recorrido/espera.png) · [Error de cierre](../evidencias/recorrido/error-pdf.png) · [Consolidado](../evidencias/recorrido/supervision.png) · [Registro HTTP del recorrido](../evidencias/recorrido/navegador.txt)

En la misma revisión comprobé las 26 operaciones de la API con 75 llamadas. También recuperé un PDF desde otro proceso de Uvicorn y comprobé que su huella SHA-256 coincidiera con la de la prueba original de esa base.

## Pruebas por requisito

| ID | Precondición o entrada principal | Resultado esperado y observado |
|---|---|---|
| PF-01 | Correo nuevo, repetido con diferentes mayúsculas y rol inyectado | Registro 201, correo repetido 409, campos extra 422 |
| PF-02 | Credenciales correctas, erróneas, JWT vencido y titular ajeno | 200, 401, 401 y 404 |
| PF-03 | Los mismos datos de alta por titular y coordinación | 403 y 201. El nuevo integrante inicia sesión |
| PF-04 | Formulario válido y formulario sin asunto | 201 con radicado y 422 sin inserción |
| PF-05 | Mismo radicado con sesión propia, ausente y ajena | 200, 401 y 404 |
| PF-06 | Cambiar asunto antes y después de iniciar revisión | 200 conservando el radicado y luego 409 |
| PF-07 | Cancelar otro caso recibido y después intentar uno en revisión | 200 con cancelación en historial y 409 |
| PF-08 | Bandeja para los dos roles, rechazo sin motivo y evaluación válida | 200 en ambas bandejas, 422 y 200 en las decisiones válidas |
| PF-09 | PDF ausente, texto que simula PDF y documento válido | 422, 415 y 200 de vuelta a En revisión |
| PF-10 | Gestor y coordinación asignan al mismo responsable | 403 y 200. El caso pasa a En atención |
| PF-11 | Consultar radicación, corrección, revisión y pasos de gestión | 200 con orden cronológico, autor y motivo |
| PF-12 | Consultar y marcar aviso propio e intentar marcarlo desde otra cuenta | 200 en consulta y lectura propia. 404 al marcar uno ajeno |
| PF-13 | Cierre sin respuesta y cierre completo | 422 y 200 con resultado persistido |
| PF-14 | Certificado expedido sin PDF, descarga propia y descarga ajena | 422, 200 con bytes iguales a los subidos y 404 |
| PF-15 | Pedir reapertura válida, repetir pendiente, intentar resolver sin permiso, aprobar y pedir fuera de plazo | 201, 409, 403, 200 y 409. El cierre anterior sigue disponible |
| PF-16 | Cierre por personal sin gestión, autorreferencia y vínculo correcto | 403, 422 y 200 con radicado principal |
| PF-17 | Configurar tres días para nuevas consultas. Simular lunes, pausa y festivo | 200 y plazo nuevo de tres días. El caso anterior conserva dos. El ejemplo vence miércoles, viernes con pausa o jueves con festivo |
| PF-18 | Combinar estado, servicio y prioridad como titular y coordinación | 403 y 200. El total y el radicado concuerdan con el filtro |

Generé las cuentas y los PDF en la verificación. La ejecución documentada en el navegador usa la misma base conservada después de la prueba de API.
