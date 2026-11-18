# Prueba de envío por WhatsApp

Probé el canal opcional RF-19 desde Meta for Developers el **18 de noviembre de 2026**. Configuré el caso de uso de WhatsApp en la aplicación Radivela, la asocié a un portfolio comercial y usé la cuenta de mensajería y el número de prueba de Meta. Registré mi teléfono como destinatario y envié la plantilla **Hola, mundo** (`hello_world`) desde el panel.

| Paso | Resultado observado |
|---|---|
| Abrí «Paso 1. Pruébalo» y preparé el remitente y el destinatario. | El número de prueba aparecía conectado. |
| Envié `hello_world` desde el panel. | El panel registró el intento. El mensaje no llegó al celular. |
| Revisé la carga útil de los webhooks de prueba. | El estado fue `failed` con el código `131031`, `Business Account locked`. |
| Abrí la cuenta en el Centro de soporte para empresas. | La cuenta aparecía como restringida, con duración «Permanente». La pantalla indicaba que debía verificar el negocio antes de enviar mensajes. |

## Resultado del envío

Resumen del webhook. Omití los identificadores, los números de teléfono y los datos internos del evento.

```json
{
  "status": "failed",
  "error": {
    "code": 131031,
    "title": "Business Account locked"
  }
}
```

**Resultado de la prueba externa:** envío fallido por la restricción de Meta. Hice la prueba desde el panel de Meta. La integración de WhatsApp con Radivela queda como ampliación opcional y los avisos implementados se consultan dentro del portal. Para repetir el envío, primero debo resolver la restricción en Meta y después comprobar que el webhook muestre `delivered`. [Referencia del código 131031](https://developers.facebook.com/documentation/business-messaging/whatsapp/support/error-codes) · [Restricciones de la plataforma](https://developers.facebook.com/documentation/business-messaging/whatsapp/policy-enforcement)
