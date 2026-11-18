# Trazabilidad y verificación de Radivela

## Revisión de las 11 imágenes

| Imagen | Exigencia | Estado |
|---|---|---|
| A1 | Completar análisis, requisitos, diseño, desarrollo, Git, pruebas y trazabilidad | Las siete etapas quedan registradas aquí. |
| A2 | Describir problema, alcance, actores, responsabilidades, proceso y CA-01 a CA-06 | El levantamiento contiene el proceso y los actores. Aquí se explicita el cruce con los seis códigos de la guía. |
| A3 | Entrevista, reglas, criterios acordados y `docs/requisitos.md` | Hay respuestas registradas y matriz RF/RNF. La especificación está en docs/requisitos.md. Registrar la aprobación académica cuando se obtenga. |
| A4 | `docs/diseno.md`, interfaces, diagramas, endpoints, validaciones, relaciones y especificación API | El diseño incluye diagramas, modelo, contratos y especificación de vistas. Los prototipos navegables y la validación visual se realizan al construir la interfaz. |
| A5 | Frontend conectado a API REST, operaciones justificadas, validaciones, persistencia, reglas e instalación reproducible | Pendiente demostrarlo en la aplicación ejecutable. Usar transiciones para cancelación y duplicados, conservando sus registros. |
| A6 | Rama, commits descriptivos, PR, historial y aportes identificables | Hay ramas propuestas. Cada RF debe tener su rama y PR hacia `main`, con commits de cambios reales, pruebas y revisión del diff. Conservar enlaces y aportes individuales verificables. |
| A7 | Ejecutar los 12 escenarios de la guía y documentar HTTP, entradas, resultados y evidencias | Los identificadores PF del levantamiento representan pruebas por RF. La tabla de este documento enumera por separado los 12 escenarios obligatorios y su cobertura. |
| A8 | `docs/trazabilidad.md` con cadena CA → RF → código → PR → prueba | El levantamiento tiene un cruce de negocio preliminar. Los seis códigos están incluidos. Incorporar los enlaces reales al implementar. |
| A9 | Ejemplo completo de trazabilidad y demostración del flujo, pruebas y aportes | Los identificadores de la imagen son ilustrativos. En este proyecto, radicar es RF-04. Registrar las rutas, PR y pruebas que efectivamente correspondan. |
| A10 | Sustentación con distribución exacta de 20 minutos | Guion registrado abajo. Falta preparar el material y ensayar con el sistema. |
| A11 | Aplicación en vivo, caso completo, decisiones, pruebas, GitHub, presentación PDF/PPT y repositorio ejecutable | Pendiente preparar y verificar esos entregables. La estudiante cubre todos los bloques del trabajo individual. |

## Correspondencia para docs/trazabilidad.md

| Condición | RF del levantamiento | Componente previsto | Escenarios mínimos de la guía | PR real |
|---|---|---|---|---|
| CA-01 Presentar solicitud | RF-04 | Formulario y API de radicación | G01, G02, G11, G12 | Pendiente |
| CA-02 Evaluar y gestionar | RF-02, RF-08 a RF-10 | Evaluación, complemento y asignación | G05, G06, G12 | Pendiente |
| CA-03 Consultar estado | RF-05, RF-08 a RF-10 | Detalle por radicado | G03, G04, G07, G12 | Pendiente |
| CA-04 Conservar intervenciones | RF-11 y acciones de gestión | Historial de atención | G08, G11, G12 | Pendiente |
| CA-05 Consultar respuesta y finalización | RF-13, RF-14 | Cierre y consulta del resultado o PDF | G09, G12 | Pendiente |
| CA-06 Consultar información consolidada | RF-17, RF-18 | Supervisión, filtros, pendientes y tiempos | G10, G12 | Pendiente |

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

Registrar por prueba el ID, RF, precondiciones, pasos, entradas, resultado esperado y observado, estado, evidencia y método/código HTTP cuando aplique. Mantener pruebas específicas para JWT, permisos, corrección, cancelación, reapertura, duplicados, cómputo de plazos, PDF y RF-19 opcional. Las pruebas aquí están pendientes de ejecución.

## Repositorio y sustentación

- Integrar `README.md`, `.gitignore`, `.env.example` cuando corresponda, código y dependencias reproducibles, preparación de datos, `docs/requisitos.md`, `docs/diseno.md`, `docs/trazabilidad.md` y evidencias reproducibles.
- El README enlaza requisitos, diseño, pruebas, trazabilidad y PR, y describe instalación, ejecución, endpoints con ejemplos y errores, aportes, conclusiones y limitaciones. Usar datos ficticios y mantener secretos fuera de Git.
- Preparar la presentación en PDF o PowerPoint y ensayar en 20 minutos. Problema y alcance (3), diseño (3), implementación (4), demostración funcional (5), pruebas con al menos un error controlado (3), GitHub y cierre (2).
- Tener la base y la aplicación listas. Mostrar el recorrido completo, decisiones técnicas, pruebas seleccionadas e historial de contribuciones. Preparar respuestas sobre lo implementado.

WhatsApp figura como RF-19 opcional. Los seis criterios obligatorios se comprueban con el portal.
## Ramas, componentes y pruebas por requisito

| RF | Función | Componente previsto | Rama | Prueba prevista | PR |
|---|---|---|---|---|---|
| RF-01 | Registro | POST /auth/registro | `feat/rf-01-alta-solicitante` | PF-01 | Pendiente |
| RF-02 | Acceso | POST /auth/login | `feat/rf-02-acceso-jwt` | PF-02 | Pendiente |
| RF-03 | Alta de personal | POST /personal | `feat/rf-03-alta-personal` | PF-03 | Pendiente |
| RF-04 | Radicación | POST /solicitudes | `feat/rf-04-radicacion` | PF-04 | Pendiente |
| RF-05 | Consulta | GET /solicitudes/{radicado} | `feat/rf-05-consulta-radicado` | PF-05 | Pendiente |
| RF-06 | Corrección | PATCH /solicitudes/{radicado} | `feat/rf-06-correccion` | PF-06 | Pendiente |
| RF-07 | Cancelación | POST /solicitudes/{radicado}/cancelar | `feat/rf-07-cancelacion` | PF-07 | Pendiente |
| RF-08 | Evaluación | GET /bandeja y POST /solicitudes/{radicado}/revision, /evaluacion | `feat/rf-08-evaluacion` | PF-08 | Pendiente |
| RF-09 | Complemento | POST /solicitudes/{radicado}/complementos | `feat/rf-09-complemento` | PF-09 | Pendiente |
| RF-10 | Asignación | POST /solicitudes/{radicado}/asignacion | `feat/rf-10-asignacion` | PF-10 | Pendiente |
| RF-11 | Historial | GET /solicitudes/{radicado}/historial | `feat/rf-11-historial` | PF-11 | Pendiente |
| RF-12 | Notificaciones | GET /avisos y PATCH /avisos/{id} | `feat/rf-12-notificaciones` | PF-12 | Pendiente |
| RF-13 | Finalización | POST /solicitudes/{radicado}/finalizacion | `feat/rf-13-finalizacion` | PF-13 | Pendiente |
| RF-14 | Entrega del PDF | GET /solicitudes/{radicado}/documentos/{id} | `feat/rf-14-respuesta-pdf` | PF-14 | Pendiente |
| RF-15 | Reapertura | POST /solicitudes/{radicado}/reaperturas y PATCH /reaperturas/{id} | `feat/rf-15-reapertura` | PF-15 | Pendiente |
| RF-16 | Duplicados | POST /solicitudes/{radicado}/duplicado | `feat/rf-16-duplicados` | PF-16 | Pendiente |
| RF-17 | Prioridades y plazos | PATCH /servicios/{id} | `feat/rf-17-prioridad-plazos` | PF-17 | Pendiente |
| RF-18 | Supervisión | GET /supervision | `feat/rf-18-supervision` | PF-18 | Pendiente |
| RF-19 | WhatsApp opcional | Avisos por WhatsApp | `feat/rf-19-avisos-whatsapp` | PF-19 | Pendiente |
