# Entrevista de levantamiento en Microsoft Teams

Realicé una entrevista escrita en Microsoft Teams con el docente Juan Carlos Morales Guerra para el proyecto 1, Sistema de gestión de solicitudes de servicio. Le pregunté cómo llegan las solicitudes, quién interviene en cada etapa y qué información se necesita para atenderlas y hacerles seguimiento.

## Capturas de la entrevista

Organicé las cinco capturas según el orden de la conversación, desde las preguntas iniciales hasta la definición de estados y plazos.

| Captura | Contenido visible |
|---|---|
| [01 · Preguntas iniciales](01-preguntas-iniciales.png) | Servicios, datos de radicación, usuarios, cuentas, permisos, revisión y etapas. |
| [02 · Continuación y JWT](02-preguntas-y-jwt.png) | Asignación, historial, cierre, reapertura, duplicados, prioridades y seguimiento. El docente indica que deben implementar JWT. |
| [03 · Respuestas del docente](03-respuestas-del-docente.png) | Servicios administrativos, ejemplo de certificado, seis campos, radicado, tres roles y alta de cuentas. |
| [04 · Revisión y seguimiento](04-flujo-y-seguimiento.png) | Validación y evaluación, asignación, cierre, corrección, cancelación, duplicados y filtros de coordinación. También inicia la consulta sobre los estados. |
| [05 · Estados y plazos](05-estados-y-plazos.png) | El docente permite inferir los estados a partir del flujo y delega la decisión sobre los plazos. |

## Respuestas que incorporé a los requisitos

| Tema | Respuesta o decisión visible | Relación con el proyecto |
|---|---|---|
| Autenticación | El docente requiere JWT. | E-05, RF-02. |
| Servicios y radicación | La organización ofrece certificados, actualización de información, solicitudes de documentos, consultas sobre trámites y peticiones generales. Para radicar se piden seis campos. Se genera un radicado y el personal puede pedir un complemento. Las imágenes no son necesarias en la radicación. | E-01 y E-02, RF-04, RF-05, RF-08, RF-09 y RF-13. |
| Roles y cuentas | Tres roles son suficientes. Una persona puede cumplir varias funciones con los permisos correspondientes. Los solicitantes se registran y el administrador da de alta al personal. | E-03 y E-04, RF-01 a RF-03. |
| Revisión y asignación | Atención comprueba si la información está completa y si el servicio se ofrece. Puede pedir información o rechazar con motivo. El titular consulta el estado y recibe avisos. Coordinación asigna. | E-06 y E-07, RF-05, RF-08 a RF-10 y RF-12. |
| Finalización y actuaciones | El responsable finaliza al registrar respuesta y resultado. El titular puede solicitar reapertura o corregir y cancelar antes de la atención. Los duplicados se cierran con justificación y conservan el historial. | E-08, RF-06, RF-07, RF-11, RF-13, RF-15 y RF-16. |
| Supervisión | Coordinación define prioridad y tiempos por tipo de trámite y consulta estado, responsable, servicio, prioridad, fechas, pendientes y tiempos. | E-09, RF-17 y RF-18. |

## Decisiones delegadas al diseño

A partir del flujo descrito por el docente, definí los estados del trámite. También establecí los plazos iniciales por tipo de servicio, el límite de diez días hábiles para solicitar una reapertura y la pausa del plazo de atención mientras el titular aporta un complemento. [Requisitos](../../docs/requisitos.md) · [Diseño técnico](../../docs/diseno.md)
