# Requisitos de Radivela

**Especificación de requisitos de la organización**  

## Problema y alcance

La organización recibe solicitudes por correo, teléfono y WhatsApp. La información queda dispersa, lo que dificulta saber si un trámite fue recibido, quién lo atiende, qué falta y cuánto tarda. Propuse centralizar la recepción, evaluación, asignación, atención, respuesta y seguimiento mediante un radicado. La organización ofrece certificados, actualización de información, solicitudes de documentos, consultas sobre trámites y peticiones generales.

## Actores y permisos

| Rol | Responsabilidad confirmada |
|---|---|
| Solicitante | Se registra por su cuenta, radica, consulta su estado, corrige o cancela antes de que empiece la atención y pide reapertura cuando necesita continuar un caso finalizado. |
| Personal de atención | Evalúa las solicitudes. El responsable asignado tramita el caso y registra la respuesta y el resultado. |
| Coordinación | Asigna casos, supervisa el proceso y define prioridades y tiempos por tipo de trámite. |

Durante la entrevista confirmé que tres roles eran suficientes y que una cuenta podía reunir permisos de varios roles. Asigné a coordinación el alta de personal.

## Registro de levantamiento

Registré las respuestas del docente en la siguiente tabla y usé el flujo descrito para definir los estados y plazos. [Capturas y resumen de Teams](../evidencias/entrevista/entrevista.md)

| Ref. | Respuesta o regla levantada | Requisitos |
|---|---|---|
| E-01 | Servicios administrativos y recorrido de un certificado, desde la solicitud hasta la respuesta y el cierre. | RF-04, RF-08, RF-10, RF-13 |
| E-02 | Seis campos de radicación, imágenes innecesarias, generación de radicado y posibilidad de pedir información o documentos faltantes. | RF-04, RF-05, RF-08, RF-09 |
| E-03 | Tres roles y posibilidad de combinar funciones mediante permisos. | RF-02, RF-03, RF-08, RF-10, RF-18 |
| E-04 | Autorregistro de solicitantes y alta de personal por el administrador. | RF-01, RF-03 |
| E-05 | JWT confirmado en el levantamiento previo. | RF-02 |
| E-06 | Atención verifica integridad y disponibilidad del servicio. Acepta, solicita complemento o rechaza con motivo. El solicitante consulta estado y recibe notificaciones. | RF-05, RF-08, RF-09, RF-12 |
| E-07 | Coordinación asigna los casos. | RF-10 |
| E-08 | El responsable registra respuesta y resultado. El solicitante puede pedir reapertura, corregir o cancelar antes de la atención. Los duplicados se cierran con justificación e historial. | RF-06, RF-07, RF-11, RF-13, RF-15, RF-16 |
| E-09 | Coordinación define prioridad y tiempos por tipo, filtra solicitudes y consulta pendientes y tiempos de atención. | RF-17, RF-18 |

## Matriz de requisitos funcionales

Formulé los criterios de aceptación a partir de la entrevista y de las reglas de diseño. Asocié una prueba funcional a cada requisito.

| ID | Función | Requisito | Criterio de aceptación | Prueba prevista | Rama propuesta |
|---|---|---|---|---|---|
| RF-01 | Registro | El solicitante crea su cuenta. El autorregistro solo concede permisos de solicitante. | Una cuenta nueva puede iniciar sesión. Un correo duplicado se rechaza. | PF-01 | `feat/rf-01-alta-solicitante` |
| RF-02 | Acceso | Autenticar con JWT y aplicar permisos por operación y recurso. | Un JWT vencido se rechaza y una cuenta autenticada no puede consultar solicitudes ajenas. | PF-02 | `feat/rf-02-acceso-jwt` |
| RF-03 | Alta de personal | Una cuenta con permiso administrativo crea cuentas internas. | Solo quien tiene el permiso puede registrar personal. Coordinación activa tiene el permiso administrativo de alta. | PF-03 | `feat/rf-03-alta-personal` |
| RF-04 | Radicación | Registrar nombre, documento, correo, tipo de servicio, asunto y descripción. Generar radicado único y persistente. | Una solicitud válida se recupera por su radicado. Si falta un dato obligatorio se rechaza el registro. Las imágenes no son necesarias. | PF-04 | `feat/rf-04-radicacion` |
| RF-05 | Consulta | El solicitante consulta el estado por radicado. | El radicado devuelve el estado actual del caso propio. La consulta exige sesión y verifica titularidad. | PF-05 | `feat/rf-05-consulta-radicado` |
| RF-06 | Corrección | El solicitante corrige un caso propio antes de que comience su atención. | Se conservan el radicado y el registro de la corrección. Después del hito de inicio se impide la edición. | PF-06 | `feat/rf-06-correccion` |
| RF-07 | Cancelación | El solicitante cancela un caso propio antes de que comience su atención. | El caso queda Cancelado y conserva su historial. Después del hito de inicio se impide cancelar. | PF-07 | `feat/rf-07-cancelacion` |
| RF-08 | Evaluación | El personal verifica que la información esté completa y que el servicio sea ofrecido. Si cumple, acepta; si está incompleta, pide información; si no corresponde a un servicio disponible, rechaza con motivo. | Coordinación y el personal habilitado para gestionar casos pueden abrir la bandeja. Coordinación ve todos los casos de revisión. El personal ve los casos sin asignar habilitados para revisión y los que tiene asignados. Cada decisión se vincula al caso. El rechazo requiere motivo y el caso aceptado queda disponible para asignación. | PF-08 | `feat/rf-08-evaluacion` |
| RF-09 | Complemento | El solicitante aporta lo pedido y el personal retoma el trámite. | El titular responde en el portal con texto o PDF según lo solicitado. Si se pidió un documento, el PDF es obligatorio. El complemento se vincula al requerimiento y el caso vuelve a En revisión. | PF-09 | `feat/rf-09-complemento` |
| RF-10 | Asignación | Coordinación asigna un caso aceptado a un responsable. | Una cuenta de coordinación asigna a un responsable habilitado y se registra quién asignó y cuándo. El personal de atención sin permiso de coordinación no asigna. | PF-10 | `feat/rf-10-asignacion` |
| RF-11 | Historial | Conservar movimientos, responsables, fechas y motivos aplicables. | Se recuperan cronológicamente las acciones del caso correcto. La visibilidad depende del rol y del permiso. | PF-11 | `feat/rf-11-historial` |
| RF-12 | Notificaciones | Informar al solicitante sobre movimientos de su caso. | El solicitante recibe los avisos definidos para su propio caso. La bandeja de avisos está dentro del portal. | PF-12 | `feat/rf-12-notificaciones` |
| RF-13 | Finalización | El responsable registra la respuesta y el resultado del trámite para finalizar. | Sin respuesta o sin resultado no se finaliza. El resultado de un caso finalizado queda disponible para su titular. | PF-13 | `feat/rf-13-finalizacion` |
| RF-14 | Entrega del PDF | Permitir enviar al solicitante un PDF como parte de la respuesta del trámite. | Para un certificado expedido se exige adjuntar el certificado en PDF antes de finalizar. En los demás trámites, o si el certificado no se expide, el PDF es opcional. El titular puede descargarlo tras iniciar sesión. El caso y el archivo conservan su vínculo y se impide el acceso de terceros. | PF-14 | `feat/rf-14-respuesta-pdf` |
| RF-15 | Reapertura | El solicitante puede pedir la reapertura de un caso finalizado. | Se registra la petición y se conserva el cierre anterior. El titular puede presentar una petición hasta el final del décimo día hábil posterior a la finalización. Se admite una petición pendiente por caso. Coordinación aprueba o rechaza con motivo. Una aprobación devuelve el caso a En atención. Un rechazo conserva el estado Finalizada. Se impiden peticiones fuera de plazo y se conserva el historial. | PF-15 | `feat/rf-15-reapertura` |
| RF-16 | Duplicados | Identificar duplicados y cerrarlos con justificación, conservando el historial. | Coordinación o la persona que gestiona ese caso puede cerrarlo por duplicado. Se exige un motivo y un radicado principal distinto, existente y del mismo solicitante. Ambos registros y sus historiales se conservan. | PF-16 | `feat/rf-16-duplicados` |
| RF-17 | Prioridades y plazos | Coordinación define prioridad y tiempo de atención por tipo de trámite. | Dos tipos pueden tener configuraciones distintas y cada caso muestra la regla aplicada. El vencimiento se calcula según la política de plazos de esta especificación. | PF-17 | `feat/rf-17-prioridad-plazos` |
| RF-18 | Supervisión | Coordinación consulta por estado, responsable, tipo, prioridad y fechas, e identifica pendientes y tiempos de atención. | Los filtros se pueden combinar. El listado, los totales y los tiempos concuerdan con los casos recuperados. | PF-18 | `feat/rf-18-supervision` |

## Decisiones de diseño incorporadas

Definí el acceso a la bandeja para coordinación y el personal de atención con permisos. Reservé el cierre por duplicado a coordinación o al responsable de gestionar el caso, y conservé el vínculo con otro radicado del mismo titular. Incorporé el envío de complementos por el portal y la entrega de respuestas en PDF. Para un certificado expedido exigí adjuntar el documento antes de finalizar. También asigné a coordinación la resolución de reaperturas.

## Requisitos no funcionales

| ID | Atributo | Criterio de verificación |
|---|---|---|
| RNF-01 | Confidencialidad y control de acceso | La API valida permisos y titularidad en cada operación protegida, incluida la descarga de PDF. Las credenciales se almacenan como hash y los secretos se gestionan fuera del repositorio. |
| RNF-02 | Integridad y consistencia | El radicado es único. El cambio de estado y su acción de historial se guardan juntos. Una operación rechazada no deja cambios parciales. |
| RNF-03 | Persistencia | Tras reiniciar la aplicación, se recuperan solicitudes, asignaciones, respuestas, notificaciones y referencias a documentos. |
| RNF-04 | Trazabilidad | Cada acción relevante guarda el autor, la fecha, el caso y el motivo o resultado cuando corresponda. El cierre, la cancelación y la eventual reapertura conservan los movimientos previos. |
| RNF-05 | Usabilidad y manejo de errores | La interfaz muestra el radicado, el estado y la siguiente acción disponible. Señala los campos inválidos sin revelar datos de otros usuarios ni detalles internos. |
| RNF-06 | Mantenibilidad y operación | La configuración, dependencias, modelo de datos e instrucciones de instalación permiten levantar el sistema en un entorno limpio con datos ficticios. |

## Flujo de atención

1. La solicitud nace **Recibida**. El personal registra **Iniciar revisión** y el caso pasa a **En revisión**. Antes de ese movimiento el titular puede corregir o cancelar. Si ambas acciones compiten con el inicio de revisión, prevalece la primera transición guardada que cumpla la regla.
2. En revisión el personal puede **aceptar** si está completa y el servicio se ofrece, pedir información y dejarla **En espera de información**, o **rechazarla** con motivo si queda fuera del catálogo. El formulario admite la opción «Otro servicio» con descripción para que el personal pueda evaluar solicitudes que no coincidan con el catálogo.
3. El titular responde desde el detalle autenticado de su solicitud. Si se pidieron aclaraciones, responde con texto. Si se pidió un documento, adjunta un PDF y puede agregar una nota. Se admite un PDF por requerimiento de documento. La API valida que el requerimiento esté abierto y que el archivo sea un PDF. La entrega queda en el historial y devuelve el caso a **En revisión**.
4. Coordinación toma el caso **Aceptado, pendiente de asignación** y lo asigna a un responsable. El caso pasa a **En atención**. El responsable registra respuesta y resultado, con PDF cuando corresponda, y el caso pasa a **Finalizada**.
5. El titular puede pedir la reapertura con motivo hasta el final del décimo día hábil posterior a la finalización. El sistema verifica el plazo al presentar la petición y admite una sola pendiente por caso. El caso sigue **Finalizada** mientras coordinación decide. Si se aprueba, vuelve a **En atención** con el mismo radicado y responsable. Si este ya no está habilitado, coordinación debe seleccionar otro al aprobar. Si se rechaza, queda **Finalizada**. La decisión, su motivo y el cierre anterior se conservan en el historial, y el titular recibe un aviso.
6. Coordinación o la persona que gestiona el caso puede cerrar un duplicado. Se considera responsable de la gestión al integrante que inició la revisión, hasta que coordinación asigne a un responsable. El cierre está disponible mientras el caso está activo. La operación exige motivo y un radicado principal existente, distinto, del mismo solicitante y que no esté cerrado por duplicado. El caso pasa a **Cerrada por duplicado**. Se registran autor, fecha, motivo y referencia al principal. El solicitante ve el motivo en su portal.
7. El sistema genera avisos en el portal para aceptación, requerimientos, rechazo, finalización y decisión de reapertura.
8. El sistema registra la fecha de radicación y de cierre, y muestra el tiempo total transcurrido y el tiempo hábil computable según la política de plazos.

## Política de plazos de atención

El docente me encargó definir los plazos como parte del diseño. Adopté las siguientes metas internas iniciales de atención. Coordinación puede modificarlas por tipo de trámite para solicitudes nuevas.

| Tipo de trámite | Prioridad inicial | Plazo |
|---|---|---:|
| Consulta sobre trámites | Normal | 2 días hábiles |
| Actualización de información | Normal | 3 días hábiles |
| Solicitud de documentos | Normal | 5 días hábiles |
| Expedición de certificados | Normal | 5 días hábiles |
| Petición general | Normal | 7 días hábiles |

- El primer día computable es el día hábil posterior a la radicación. El vencimiento ocurre al terminar el último día computable, en la zona horaria de Colombia.
- Son hábiles los días de lunes a viernes, con exclusión de las fechas festivas registradas en el calendario del sistema. No se consumen días hábiles mientras el caso está En espera de información. Si un día computable ya empezó antes de la pausa, ese día se cuenta. El conteo se reanuda el primer día hábil posterior a la entrega del complemento.
- La prioridad y el plazo se guardan al radicar. Los cambios posteriores de configuración se aplican a casos nuevos. La prioridad inicial es Normal para todos los tipos porque el cliente no identificó trámites urgentes. Coordinación puede configurar las prioridades Baja, Normal o Alta por tipo.
- El cierre detiene el conteo y conserva el resultado del tramo inicial. Si se aprueba una reapertura, se inicia un tramo de atención con el mismo plazo guardado y el primer día hábil posterior a la aprobación como inicio del conteo.
- Coordinación puede filtrar por fecha de radicación o de cierre y distinguir casos pendientes en plazo y vencidos. El tiempo total transcurrido incluye las esperas.
- Verificación de RF-17: con un calendario sin festivos en el intervalo, una consulta radicada el lunes vence al finalizar el miércoles. Si entra en espera el lunes y se complementa el miércoles, vence al finalizar el viernes. Un cambio posterior a tres días no altera el plazo de dos días del caso ya radicado.

## Ampliación opcional | Avisos por WhatsApp

**RF-19 — Notificar por WhatsApp.** Enviar avisos automáticos de información pendiente y de respuesta disponible mediante WhatsApp Business Platform (Cloud API). El solicitante proporciona su número y acepta recibir avisos de forma voluntaria. Puede desactivar el canal. El mensaje dirige al portal autenticado. Los documentos, motivos y datos personales se consultan allí.

**Criterio de aceptación.** Un evento genera el aviso en el portal y, si el canal está habilitado y el destinatario ha dado su consentimiento, registra un envío por WhatsApp mediante una plantilla aprobada. Al desactivar el canal se omiten los nuevos envíos. Si Meta rechaza un envío, se registra el fallo y el trámite y su aviso en el portal siguen disponibles. Controlar duplicados por evento y destinatario. Rama propuesta: `feat/rf-19-avisos-whatsapp`. Prueba prevista: PF-19.

**Activación.** Requiere configurar la cuenta y el número de WhatsApp Business, credenciales fuera del repositorio y plantillas aprobadas. Validar primero con un número de prueba y habilitar después de verificar el flujo principal. Referencia: [WhatsApp Business Platform, Meta](https://developers.facebook.com/documentation/business-messaging/whatsapp/overview).

## Arquitectura

Frontend web conectado a API REST en FastAPI con Python y Pydantic. JWT para autenticación y verificación de permisos en el servidor. Se propone SQLite con SQLAlchemy y migraciones para el entorno inicial. Entidades candidatas: Usuario, Área, TipoServicio, Solicitud, AcciónAtención, RequerimientoInformación, Documento, Notificación y PeticiónReapertura. El PDF de respuesta tendrá acceso controlado por la API. La implementación del almacenamiento, tamaño y validación del archivo se definirá en diseño.

## Trazabilidad del proceso

| Resultado de negocio | Requisitos | Evidencia prevista |
|---|---|---|
| Registrar una solicitud y recuperar su radicado | RF-04, RF-05 | Radicación válida, rechazo por dato inválido, consulta válida y consulta inexistente. |
| Evaluar y gestionar con autorización | RF-02, RF-06 a RF-10, RF-15, RF-16 | Evaluación y complemento, asignación por coordinación, rechazo a rol sin permiso y validación de transiciones. |
| Consultar el estado y conservar intervenciones | RF-05, RF-11, RF-12 | Consulta del estado actual, historial cronológico, aviso visible y persistencia tras reiniciar. |
| Consultar la respuesta final | RF-13, RF-14 | Cierre con resultado y descarga del PDF como titular. Prueba de acceso denegado para terceros. |
| Supervisar solicitudes y tiempos | RF-17, RF-18 | Filtros combinados, pendientes y tiempos calculados con registros conocidos. |
| Verificar integración | RNF-02 a RNF-05 | Recorrido desde formulario hasta respuesta y supervisión con datos persistidos. |

## Control de implementación

Una rama y un pull request hacia `main` por requisito funcional. El PR debe identificar el requisito, los cambios realizados, los resultados obtenidos y sus evidencias. Registrar el enlace del PR en la matriz de trazabilidad al integrarlo. Las pruebas están previstas y sus resultados se registrarán durante la ejecución.
