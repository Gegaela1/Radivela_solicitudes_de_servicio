# Pruebas de Radivela

`python -m pytest -q -s` migra una base SQLite temporal y ejecuta los escenarios HTTP con cuentas ficticias. Dejé las entradas completas, las precondiciones y las aserciones en el código de prueba. Guardé la salida de ejecución en [evidencia HTTP](../evidencias/evidencia-http.txt).

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

Los PDF y las cuentas de prueba se generan durante la ejecución. El flujo de navegador y la prueba HTTP usan bases de prueba distintas.
