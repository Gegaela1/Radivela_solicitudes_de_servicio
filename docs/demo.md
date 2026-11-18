# Demostración de Radivela

Después de migrar una base de demostración con `alembic upgrade head`, ejecuta `python -m scripts.demo`. Escribe una contraseña local de al menos diez caracteres. El script crea cuentas ficticias y un PDF de muestra en la carpeta de almacenamiento.

| Perfil | Cuenta de ejemplo | Vista inicial |
|---|---|---|
| Solicitante | `ana@example.com` | Mis solicitudes |
| Atención | `atencion@example.com` | Bandeja |
| Coordinación | `coord@example.com` | Bandeja con acceso a supervisión |

Si olvidaste la contraseña, ejecuta `& $python -m scripts.demo --restablecer` desde la carpeta del proyecto. Introduce y confirma una clave nueva. El comando cambia la contraseña de las tres cuentas ficticias existentes y conserva las solicitudes. Cierra sesión en el navegador antes de entrar con la nueva contraseña.

Abre tres perfiles o ventanas de navegador para conservar las tres sesiones. En vivo, radica un certificado, solicita una aclaración, contéstala, acepta, asigna, intenta finalizar sin el PDF, adjúntalo, cierra y muestra la descarga y la supervisión.

| Tiempo | Bloque | Qué mostrar |
|---|---|---|
| 0–3 min | Problema y alcance | Canales dispersos, radicado único y responsabilidades |
| 3–6 min | Diseño | Estados, permisos y manejo de esperas |
| 6–10 min | Implementación | Interfaz y API, migraciones, JWT, Argon2 y almacenamiento |
| 10–15 min | Demostración | Certificado con complemento, asignación, finalización y descarga |
| 15–18 min | Pruebas | Error 422 al cerrar certificado expedido sin PDF y reporte de ejecución |
| 18–20 min | GitHub y cierre | Un requisito en la matriz, su rama y el historial |

## G12 automatizado

Arranca la aplicación con las cuentas ficticias. Instala Playwright Core con Node.js y usa Microsoft Edge o una ruta a otro Chromium compatible.

```powershell
npm install --no-save playwright-core
$env:RADIVELA_DEMO_PASSWORD = Read-Host 'Contraseña local de cuentas ficticias' -MaskInput
$env:RADIVELA_DEMO_PDF = (Resolve-Path storage/certificado-ficticio.pdf).Path
$env:RADIVELA_SCREENSHOT = "$PWD\storage\g12.png"
node tests/browser/recorrido.cjs
```

Para guardar también las capturas de la espera de información, el error de cierre y supervisión, asigna un directorio a `RADIVELA_FLOW_SCREENSHOTS`. Las llamadas HTTP aparecen en la consola. La captura muestra el resultado del certificado como titular. Si el servidor usa otro puerto, asigna su dirección a `RADIVELA_BROWSER_URL`. Si usas otro Chromium, asigna el ejecutable a `RADIVELA_BROWSER_PATH`. Para consultar una ejecución persistente de las pruebas de API, sigue [casos guardados](pruebas.md#evidencia-por-endpoint-y-casos-guardados).
