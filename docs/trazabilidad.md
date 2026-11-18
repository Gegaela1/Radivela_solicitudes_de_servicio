# Trazabilidad y verificación de Radivela

## Revisión de las 11 imágenes

| Imagen | Exigencia | Estado |
|---|---|---|
| A1 | Completar análisis, requisitos, diseño, desarrollo, Git, pruebas y trazabilidad | Registré las siete etapas en esta matriz. |
| A2 | Describir problema, alcance, actores, responsabilidades, proceso y CA-01 a CA-06 | Documenté el proceso y los actores y los relacioné con los seis criterios de la guía. |
| A3 | Entrevista, reglas, criterios acordados y `docs/requisitos.md` | Registré la [entrevista](../evidencias/entrevista/entrevista.md) y documenté los criterios en la [especificación](requisitos.md). |
| A4 | `docs/diseno.md`, interfaces, diagramas, endpoints, validaciones, relaciones y especificación API | Documenté los diagramas, el modelo, los contratos y las vistas. Verifiqué la interfaz con el recorrido de navegador. |
| A5 | Frontend conectado a API REST, operaciones justificadas, validaciones, persistencia, reglas e instalación reproducible | Comprobé la aplicación ejecutable en G12. Implementé la cancelación y el cierre de duplicados como transiciones que conservan sus registros. |
| A6 | Rama, commits descriptivos, PR, historial y aportes identificables | Organicé los 18 requisitos en ramas y commits locales. Integré los cambios mediante los PR enlazados en esta matriz. |
| A7 | Ejecutar los 12 escenarios de la guía y documentar HTTP, entradas, resultados y evidencias | Los identificadores PF del levantamiento representan pruebas por RF. La tabla de este documento enumera por separado los 12 escenarios obligatorios y su cobertura. |
| A8 | `docs/trazabilidad.md` con cadena CA → RF → código → PR → prueba | Relacioné CA-01 a CA-06 con los requisitos, las rutas y las pruebas de la tabla. |
| A9 | Ejemplo completo de trazabilidad y demostración del flujo, pruebas y aportes | Vinculé la radicación (RF-04) con el formulario, `POST /api/v1/solicitudes` y su registro de prueba. |
| A10 | Sustentación con distribución exacta de 20 minutos | Preparé el [guion](demo.md) para la presentación y ejecuté el recorrido funcional en el navegador. |
| A11 | Aplicación en vivo, caso completo, decisiones, pruebas, GitHub, presentación PDF/PPT y repositorio ejecutable | Preparé el repositorio, la presentación y las evidencias del caso en navegador para mi sustentación individual. |

## Correspondencia para docs/trazabilidad.md

| Condición | RF del levantamiento | Componente | Escenarios mínimos de la guía | PR real |
|---|---|---|---|---|
| CA-01 Presentar solicitud | RF-04 | Formulario **Nueva solicitud** y `POST /api/v1/solicitudes` | G01, G02, G11, G12 | [RF-04](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/4) |
| CA-02 Evaluar y gestionar | RF-02, RF-08 a RF-10 | Bandeja y acciones `/revision`, `/evaluacion`, `/complementos` y `/asignacion` | G05, G06, G12 | [RF-02](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/2), [RF-08](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/8), [RF-09](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/9), [RF-10](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/10) |
| CA-03 Consultar estado | RF-05, RF-08 a RF-10 | Detalle y `GET /api/v1/solicitudes/{radicado}` | G03, G04, G07, G12 | [RF-05](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/5), [RF-08](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/8), [RF-09](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/9), [RF-10](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/10) |
| CA-04 Conservar intervenciones | RF-11 y acciones de gestión | Historial y `GET /api/v1/solicitudes/{radicado}/historial` | G08, G11, G12 | [RF-11](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/11) |
| CA-05 Consultar respuesta y finalización | RF-13, RF-14 | `POST /api/v1/solicitudes/{radicado}/finalizacion` y descarga `/documentos/{document_id}` | G09, G12 | [RF-13](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/13), [RF-14](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/14) |
| CA-06 Consultar información consolidada | RF-17, RF-18 | Vista **Supervisión** y `GET /api/v1/supervision` | G10, G12 | [RF-17](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/17), [RF-18](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/18) |

## 12 escenarios obligatorios de la guía

| ID de control | Escenario | Evidencia esperada |
|---|---|---|
| G01 | Registrar solicitud válida | Radicado persistido y recuperable. |
| G02 | Registrar con datos inválidos | Respuesta controlada y ausencia de registro inválido. |
| G03 | Consultar solicitud existente | Datos correspondientes al caso. |
| G04 | Consultar solicitud inexistente | Error controlado. |
| G05 | Gestionar como actor autorizado | Acción válida y cambio registrado. |
| G06 | Intentar gestionar sin autorización | Operación impedida sin modificar el caso. |
| G07 | Consultar estado | Estado consistente con las acciones. |
| G08 | Consultar historial | Intervenciones del caso correcto. |
| G09 | Finalizar y recuperar el resultado | Respuesta accesible para el titular. |
| G10 | Consultar el consolidado | Resumen consistente de varias solicitudes. |
| G11 | Verificar persistencia e integridad | Datos conservados tras reinicio y relaciones válidas. |
| G12 | Demostrar integración completa | Recorrido en el navegador que pasa por API y base de datos. |

Registrar por prueba el ID, RF, precondiciones, pasos, entradas, resultado esperado y observado, estado, evidencia y método/código HTTP cuando aplique. Mantener pruebas específicas para JWT, permisos, corrección, cancelación, reapertura, duplicados, cómputo de plazos, PDF y RF-19 opcional. Los resultados observados se registran en [Pruebas de Radivela](pruebas.md).

## Repositorio y sustentación

- Integrar `README.md`, `.gitignore`, `.env.example` cuando corresponda, código y dependencias reproducibles, preparación de datos, `docs/requisitos.md`, `docs/diseno.md`, `docs/trazabilidad.md` y evidencias reproducibles.
- El README enlaza requisitos, diseño, pruebas, trazabilidad y PR, y describe instalación, ejecución, endpoints con ejemplos y errores, aportes, conclusiones y limitaciones. Usar datos ficticios y mantener secretos fuera de Git.
- Preparar la presentación en PDF o PowerPoint y ensayar en 20 minutos. Problema y alcance (3), diseño (3), implementación (4), demostración funcional (5), pruebas con al menos un error controlado (3), GitHub y cierre (2).
- Tener la base y la aplicación listas. Mostrar el recorrido completo, decisiones técnicas, pruebas seleccionadas e historial de contribuciones. Preparar respuestas sobre lo implementado.

WhatsApp figura como RF-19 opcional. Los seis criterios obligatorios se comprueban con el portal.
## Ramas, componentes y pruebas por requisito

| RF | Función | Componente | Rama | Prueba ejecutada | PR |
|---|---|---|---|---|---|
| RF-01 | Registro | POST /auth/registro | `feat/rf-01-alta-solicitante` | PF-01 | [PR #1](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/1) |
| RF-02 | Acceso | POST /auth/login | `feat/rf-02-acceso-jwt` | PF-02 | [PR #2](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/2) |
| RF-03 | Alta de personal | POST /personal | `feat/rf-03-alta-personal` | PF-03 | [PR #3](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/3) |
| RF-04 | Radicación | POST /solicitudes | `feat/rf-04-radicacion` | PF-04 | [PR #4](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/4) |
| RF-05 | Consulta | GET /solicitudes/{radicado} | `feat/rf-05-consulta-radicado` | PF-05 | [PR #5](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/5) |
| RF-06 | Corrección | PATCH /solicitudes/{radicado} | `feat/rf-06-correccion` | PF-06 | [PR #6](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/6) |
| RF-07 | Cancelación | POST /solicitudes/{radicado}/cancelar | `feat/rf-07-cancelacion` | PF-07 | [PR #7](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/7) |
| RF-08 | Evaluación | GET /bandeja y POST /solicitudes/{radicado}/revision, /evaluacion | `feat/rf-08-evaluacion` | PF-08 | [PR #8](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/8) |
| RF-09 | Complemento | POST /solicitudes/{radicado}/complementos | `feat/rf-09-complemento` | PF-09 | [PR #9](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/9) |
| RF-10 | Asignación | POST /solicitudes/{radicado}/asignacion | `feat/rf-10-asignacion` | PF-10 | [PR #10](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/10) |
| RF-11 | Historial | GET /solicitudes/{radicado}/historial | `feat/rf-11-historial` | PF-11 | [PR #11](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/11) |
| RF-12 | Notificaciones | GET /avisos y PATCH /avisos/{id} | `feat/rf-12-notificaciones` | PF-12 | [PR #12](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/12) |
| RF-13 | Finalización | POST /solicitudes/{radicado}/finalizacion | `feat/rf-13-finalizacion` | PF-13 | [PR #13](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/13) |
| RF-14 | Entrega del PDF | GET /solicitudes/{radicado}/documentos/{id} | `feat/rf-14-respuesta-pdf` | PF-14 | [PR #14](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/14) |
| RF-15 | Reapertura | POST /solicitudes/{radicado}/reaperturas y PATCH /reaperturas/{id} | `feat/rf-15-reapertura` | PF-15 | [PR #15](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/15) |
| RF-16 | Duplicados | POST /solicitudes/{radicado}/duplicado | `feat/rf-16-duplicados` | PF-16 | [PR #16](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/16) |
| RF-17 | Prioridades y plazos | PATCH /servicios/{id} | `feat/rf-17-prioridad-plazos` | PF-17 | [PR #17](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/17) |
| RF-18 | Supervisión | GET /supervision | `feat/rf-18-supervision` | PF-18 | [PR #18](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio/pull/18) |
| RF-19 | WhatsApp opcional | Prueba externa desde Meta | — | [Envío externo fallido (131031)](../evidencias/whatsapp.md) | — |


## Código y evidencia

La implementación de los contratos de la matriz está en [app/routes.py](../app/routes.py). Las vistas que llaman a esos contratos están en [app/web/portal.js](../app/web/portal.js). [Pruebas de Radivela](pruebas.md) enlaza las evidencias de los escenarios G01 a G12 y PF-01 a PF-18. El [índice de evidencias de la API](../evidencias/api/indice.md) enlaza una evidencia por endpoint.

Cada rama de la matriz apunta al commit que incorpora el requisito. Enlacé los PR de cada requisito en el [repositorio confirmado](https://github.com/Gegaela1/Radivela_solicitudes_de_servicio).
