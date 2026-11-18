const assert = require("node:assert/strict");
const { chromium } = require("playwright-core");

const start = process.env.RADIVELA_BROWSER_URL || "http://127.0.0.1:8000";
const password = process.env.RADIVELA_DEMO_PASSWORD;
const pdf = process.env.RADIVELA_DEMO_PDF;
const screenshot = process.env.RADIVELA_SCREENSHOT;
const browserPath = process.env.RADIVELA_BROWSER_PATH;
if (!password || !pdf) throw new Error("Configure RADIVELA_DEMO_PASSWORD y RADIVELA_DEMO_PDF.");

async function main() {
  const browser = await chromium.launch({
    executablePath: browserPath, channel: browserPath ? undefined : "msedge",
    args: ["--disable-gpu"],
  });
  try {
    const errors = [];
    async function login(email) {
      const context = await browser.newContext();
      const page = await context.newPage();
      page.on("pageerror", error => errors.push(error.message));
      page.on("response", response => {
        if (response.url().includes("/api/v1/")) {
          console.log("G12", response.request().method(), new URL(response.url()).pathname,
            "HTTP", response.status());
        }
      });
      await page.goto(start);
      const panel = page.locator("section").filter({
        has: page.getByRole("heading", { name: "Iniciar sesión", exact: true }),
      }).filter({ has: page.getByRole("button", { name: "Ingresar" }) }).last();
      await panel.getByLabel("Correo electrónico").fill(email);
      await panel.getByLabel("Contraseña").fill(password);
      await panel.getByRole("button", { name: "Ingresar" }).click();
      await page.getByRole("link", { name: "Avisos", exact: true }).waitFor();
      return page;
    }
    async function action(page, name, fill) {
      const summary = page.locator("summary").getByText(name, { exact: true });
      await summary.click();
      const form = page.locator("details[open] form");
      if (fill) await fill(form);
      await form.getByRole("button", { name, exact: true }).click();
      await page.getByRole("status").getByText("Cambio guardado.", { exact: true }).waitFor();
    }
    function state(page, value) {
      return page.locator(".heading .status").getByText(value, { exact: true }).waitFor();
    }

    const owner = await login("ana@example.com");
    await owner.getByRole("link", { name: "Nueva solicitud" }).click();
    await owner.getByLabel("Nombre", { exact: true }).fill("Ana Solís (demo)");
    await owner.getByLabel("Documento", { exact: true }).fill("D-01");
    await owner.getByLabel("Correo electrónico").fill("ana@example.com");
    await owner.getByLabel("Tipo de servicio").selectOption({ label: "Expedición de certificados" });
    await owner.getByLabel("Asunto").fill("Certificado para la demostración");
    await owner.getByLabel("Descripción").fill("Solicito el certificado de un trámite ficticio.");
    await owner.getByRole("button", { name: "Radicar solicitud" }).click();
    const receipt = owner.getByRole("heading", { name: /^RAD-/ });
    const radicado = await receipt.textContent();
    await owner.getByRole("link", { name: radicado }).click();
    await state(owner, "Recibida");

    const handler = await login("atencion@example.com");
    await handler.getByRole("link", { name: radicado }).click();
    await action(handler, "Iniciar revisión");
    await state(handler, "En revisión");
    await action(handler, "Evaluar solicitud", async form => {
      await form.getByLabel("Decisión").selectOption("requerir");
      await form.getByLabel("Motivo").fill("Indique el periodo solicitado.");
      await form.getByLabel("Tipo de complemento").selectOption("texto");
    });
    await state(handler, "En espera de información");

    await owner.reload();
    await action(owner, "Responder requerimiento", form => form.getByLabel("Respuesta").fill("Periodo 2026."));
    await state(owner, "En revisión");
    await handler.reload();
    await action(handler, "Evaluar solicitud");
    await state(handler, "Aceptada");

    const coordinator = await login("coord@example.com");
    await coordinator.getByRole("link", { name: radicado }).click();
    await action(coordinator, "Asignar responsable", form =>
      form.getByLabel("Responsable").selectOption({ label: "Darío Vega (demo)" }));
    await state(coordinator, "En atención");
    await handler.reload();
    await handler.locator("summary").getByText("Finalizar atención", { exact: true }).click();
    const closure = handler.locator("details[open] form");
    await closure.getByLabel("Respuesta").fill("Certificado de demostración disponible.");
    await closure.getByRole("button", { name: "Finalizar atención" }).click();
    await handler.getByRole("status").getByText("Adjunte el certificado en PDF").waitFor();
    await closure.getByLabel("Archivo PDF").setInputFiles(pdf);
    await closure.getByRole("button", { name: "Finalizar atención" }).click();
    await state(handler, "Finalizada");

    await owner.reload();
    await state(owner, "Finalizada");
    await owner.getByText("Certificado de demostración disponible.", { exact: true }).waitFor();
    const [download] = await Promise.all([
      owner.waitForEvent("download"),
      owner.getByRole("button", { name: "respuesta.pdf", exact: true }).click(),
    ]);
    assert.equal(download.suggestedFilename(), "respuesta.pdf");
    const firstBody = await owner.locator("main").innerText();
    assert.match(firstBody, /Complemento recibido/);
    if (screenshot) await owner.screenshot({ path: screenshot, fullPage: true });
    await coordinator.getByRole("link", { name: "Supervisión" }).click();
    await coordinator.getByRole("link", { name: radicado }).waitFor();
    await owner.getByRole("link", { name: "Mis solicitudes", exact: true }).click();
    const row = owner.getByRole("row").filter({ hasText: radicado });
    await row.getByRole("link", { name: "Ver respuesta" }).waitFor();
    assert.equal(await row.getByRole("progressbar").getAttribute("value"), "100");
    if (process.env.RADIVELA_LIST_SCREENSHOT) {
      await owner.screenshot({ path: process.env.RADIVELA_LIST_SCREENSHOT, fullPage: true });
    }
    assert.deepEqual(errors, []);
    console.log("G12 OK", radicado, "finalizado, con PDF y visible en supervisión.");
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
