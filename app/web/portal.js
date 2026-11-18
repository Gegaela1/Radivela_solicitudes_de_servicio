"use strict";

const content = document.querySelector("#content");
const nav = document.querySelector("#nav");
const profile = document.querySelector("#profile");
const sessionActions = document.querySelector("#session-actions");
const stageProgress = {
  "Recibida": 10, "En revisión": 30, "En espera de información": 40,
  "Aceptada": 50, "En atención": 60, "Finalizada": 100,
};
const feedback = document.querySelector("#feedback");
const states = ["Recibida", "En revisión", "En espera de información", "Aceptada",
  "En atención", "Finalizada", "Cancelada", "Rechazada", "Cerrada por duplicado"];
let session = JSON.parse(sessionStorage.getItem("radivela-session") || "null");
let catalog = [];
let fieldId = 0;

function el(tag, value, attrs = {}) {
  const element = document.createElement(tag);
  if (value != null) element.textContent = value;
  for (const [key, attr] of Object.entries(attrs)) element.setAttribute(key, attr);
  return element;
}

function message(text, error = false) {
  feedback.textContent = text;
  feedback.classList.toggle("error", error);
}

async function api(path, method = "GET", body) {
  const headers = session ? { Authorization: "Bearer " + session.access_token } : {};
  if (body && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(body);
  }
  const result = await fetch("/api/v1" + path, { method, headers, body });
  if (result.ok) {
    return result.headers.get("content-type").startsWith("application/pdf")
      ? result.blob() : result.json();
  }
  if (result.status === 401 && session) {
    session = null;
    sessionStorage.removeItem("radivela-session");
    access();
  }
  const data = await result.json().catch(() => ({}));
  const error = new Error(typeof data.detail === "string" ? data.detail :
    "Revise los campos indicados. Código HTTP " + result.status + ".");
  error.fields = Array.isArray(data.detail) ? data.detail : [];
  throw error;
}

function button(title, action, className = "secondary") {
  const element = el("button", title, { type: "button", class: className });
  element.onclick = async () => {
    try { await action(); } catch (error) { message(error.message, true); }
  };
  return element;
}

function card(title) {
  const section = el("section", null, { class: "card" });
  section.append(el("h2", title));
  return section;
}

function link(label, route, className) {
  return el("a", label, { href: "#" + route, ...(className ? { class: className } : {}) });
}

function heading(title, action) {
  const wrapper = el("div", null, { class: "heading" });
  wrapper.append(el("h1", title));
  if (action) wrapper.append(action);
  content.append(wrapper);
}

function field(name, label, type = "text", options = {}) {
  return { name, label, type, ...options };
}

function buildForm(fields, title, handler, className) {
  const form = el("form", null, className ? { class: className } : {});
  const inputs = {};
  for (const spec of fields) {
    const label = el("label", spec.label);
    const control = spec.type === "select" ? el("select") :
      spec.type === "textarea" ? el("textarea") : el("input", null, { type: spec.type });
    control.name = spec.name;
    control.required = !spec.optional;
    if (spec.placeholder) control.placeholder = spec.placeholder;
    if (spec.type === "select") {
      if (spec.optional) control.append(el("option", "—", { value: "" }));
      for (const option of spec.options) control.append(el("option", option[1], { value: option[0] }));
    }
    if (spec.type === "file") control.accept = "application/pdf,.pdf";
    if (spec.type === "password") control.autocomplete = spec.min ? "new-password" : "current-password";
    if (spec.min != null) {
      if (spec.type === "number") control.min = spec.min;
      else control.minLength = spec.min;
    }
    if (spec.value != null) control.value = spec.value;
    const error = el("span", "", { class: "field-error", id: "error-" + String(++fieldId) });
    control.setAttribute("aria-describedby", error.id);
    inputs[spec.name] = { control, error };
    label.append(control, error);
    form.append(label);
  }
  const submit = el("button", title, { type: "submit" });
  form.append(submit);
  form.onsubmit = async event => {
    event.preventDefault();
    submit.disabled = true;
    message("Procesando…");
    const values = {};
    for (const spec of fields) {
      const { control, error } = inputs[spec.name];
      control.removeAttribute("aria-invalid");
      error.textContent = "";
      const value = spec.type === "file" ? control.files[0] : control.value;
      if (value != null && value !== "") {
        values[spec.name] = spec.type === "number" || spec.numeric ? Number(value) : value;
      }
    }
    try {
      await handler(values);
    } catch (error) {
      message(error.message, true);
      for (const item of error.fields || []) {
        const target = inputs[item.loc[1]];
        if (target) {
          target.error.textContent = item.msg;
          target.control.setAttribute("aria-invalid", "true");
        }
      }
    } finally {
      submit.disabled = false;
    }
  };
  return form;
}

const email = field("correo", "Correo electrónico", "email");
const password = field("contrasena", "Contraseña", "password");
const nameField = field("nombre", "Nombre");
const idField = field("documento", "Documento");
const makeAccount = [nameField, idField, email, { ...password, min: 10 }];

function access() {
  nav.hidden = true;
  profile.hidden = true;
  sessionActions.replaceChildren();
  content.replaceChildren();
  heading("Acceso al portal");
  const layout = el("div", null, { class: "access" });
  const login = card("Iniciar sesión");
  login.append(buildForm([email, password], "Ingresar", async values => {
    session = await api("/auth/login", "POST", values);
    sessionStorage.setItem("radivela-session", JSON.stringify(session));
    catalog = await api("/servicios");
    const destination = session.roles.includes("solicitante") ? "mis-solicitudes" : "bandeja";
    if (location.hash === "#" + destination) await render();
    else location.hash = destination;
  }));
  const register = card("Crear cuenta de solicitante");
  register.append(buildForm(makeAccount, "Registrarme", async values => {
    await api("/auth/registro", "POST", values);
    register.querySelector("form").reset();
    message("Cuenta creada. Ya puedes iniciar sesión.");
  }));
  layout.append(login, register);
  content.append(layout);
}

function options(values) { return values.map(value => [value, value]); }
function serviceField(optional = false, values = catalog) {
  return field("servicio_id", "Tipo de servicio", "select", {
    options: values.map(item => [item.id, item.nombre]), numeric: true, optional,
  });
}
function submission(entry = {}) {
  return [nameField, idField, email, serviceField(), field("asunto", "Asunto"),
    field("descripcion", "Descripción", "textarea")].map(spec =>
    ({ ...spec, value: entry[spec.name] }));
}
function status(value) { return el("span", value, { class: "status", "data-state": value }); }
function dateText(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("es-CO", {
    dateStyle: "medium", timeStyle: "short", timeZone: "America/Bogota",
  }).format(new Date(value));
}
function caseLink(entry) { return link(entry.radicado, "caso/" + entry.radicado); }

function progressFor(state) {
  const value = stageProgress[state];
  if (value == null) return "—";
  const widget = el("div", null, { class: "progress" });
  widget.append(el("span", value + " %"), el("progress", null, {
    value, max: 100, "aria-label": "Avance por etapa",
  }));
  return widget;
}

function table(rows, supervision = false, personal = false) {
  if (!rows.length) return el("p", "No hay solicitudes para mostrar.", { class: "muted" });
  const columns = personal ? ["Radicado", "Trámite", "Fecha", "Progreso", "Estado", "Acciones"] :
    ["Radicado", "Asunto", "Estado", "Fecha", ...(supervision ?
      ["Prioridad", "Días hábiles", "Vencimiento", "Tiempo total (h)"] : [])];
  const table = el("table");
  const frame = el("div", null, { class: "table-frame" });
  const headings = el("tr");
  const head = el("thead");
  const body = el("tbody");
  for (const column of columns) headings.append(el("th", column, { scope: "col" }));
  head.append(headings);
  for (const item of rows) {
    const row = el("tr");
    const label = catalog.find(service => service.id === item.servicio_id)?.nombre;
    const procedure = el("div");
    procedure.append(el("strong", label || item.asunto));
    if (label) procedure.append(el("small", item.asunto, { class: "muted" }));
    const isWaiting = item.estado === "En espera de información";
    const text = { Finalizada: "Ver respuesta", "En espera de información":
      item.tipo_requerimiento === "documento" ? "Adjuntar PDF" : "Responder" }[item.estado];
    const action = el("div", null, { class: "table-actions" });
    const destination = "caso/" + item.radicado;
    action.append(link(text || "Ver detalle", destination + (isWaiting ? "/complemento" : ""),
      isWaiting ? "primary" : "primary secondary"));
    const shortDate = new Intl.DateTimeFormat("es-CO", {
      dateStyle: "medium", timeZone: "America/Bogota",
    }).format(new Date(item.creada));
    const values = personal ? [caseLink(item), procedure, shortDate, progressFor(item.estado),
      status(item.estado), action] : [caseLink(item), item.asunto, status(item.estado), dateText(item.creada)];
    if (supervision) values.push(item.prioridad, item.dias_habiles, item.vencimiento || "En pausa",
      (item.segundos_totales / 3600).toFixed(1));
    values.forEach((value, i) => {
      const cell = el("td", null, { "data-label": columns[i] });
      cell.append(value);
      row.append(cell);
    });
    body.append(row);
  }
  table.append(head, body);
  frame.append(table);
  return frame;
}

async function listing(path, target, params = {}, supervision = false) {
  const limit = 20;
  async function page(offset) {
    const query = new URLSearchParams({ ...params, offset, limite: limit });
    const response = await api(path + "?" + query);
    const rows = supervision ? response.solicitudes : response;
    target.replaceChildren();
    if (supervision) {
      const average = response.promedio_dias_habiles_cerradas;
      target.append(el("p", response.total + " casos · " + response.pendientes + " pendientes · " +
        response.en_plazo + " en plazo · " + response.vencidas + " vencidos · " +
        (average == null ? "Sin cierres" : average.toFixed(1) + " días hábiles por cierre")));
    }
    target.append(table(rows, supervision, path === "/solicitudes"));
    if (offset > 0) target.append(button("Anterior", () => page(offset - limit)));
    if (supervision ? offset + limit < response.total : rows.length === limit) {
      target.append(button("Siguiente", () => page(offset + limit)));
    }
    message("");
  }
  await page(0);
}

async function own() {
  heading("Mis solicitudes", link("Nueva solicitud", "nueva", "primary new-case"));
  content.append(buildForm([field("radicado", "Buscar por radicado", "text", { placeholder: "Ingresa el número de radicado" })], "Buscar", async values => {
    const result = await api("/solicitudes/" + encodeURIComponent(values.radicado.trim()));
    location.hash = "caso/" + result.radicado;
  }, "filters search"));
  const results = el("div");
  content.append(results);
  await listing("/solicitudes", results);
}

function newCase() {
  heading("Nueva solicitud");
  const panel = card("Datos de radicación");
  panel.append(buildForm(submission(), "Radicar solicitud", async values => {
    const result = await api("/solicitudes", "POST", values);
    content.replaceChildren();
    heading("Solicitud radicada");
    const receipt = card(result.radicado);
    receipt.append(button("Copiar radicado", async () => {
      await navigator.clipboard.writeText(result.radicado);
      message("Radicado copiado.");
    }), " ", caseLink(result));
    content.append(receipt);
    message("La solicitud quedó Recibida.");
  }));
  content.append(panel);
}

async function caseView(radicado, openComplement = false) {
  const path = "/solicitudes/" + encodeURIComponent(radicado);
  const [entry, history] = await Promise.all([api(path), api(path + "/historial")]);
  heading(entry.asunto, status(entry.estado));
  const overview = card(entry.radicado);
  overview.append(el("p", entry.servicio + " · " + dateText(entry.creada), { class: "muted" }),
    el("p", entry.descripcion, { class: "detail-text" }),
    el("p", entry.nombre + " · " + entry.documento + " · " + entry.correo),
    el("p", "Prioridad " + entry.prioridad + " · " + entry.dias + " días hábiles" +
      (entry.vencimiento ? " · Vence " + entry.vencimiento : "")));
  if (entry.principal) overview.append("Radicado principal ", link(entry.principal, "caso/" + entry.principal));
  if (entry.requerimiento) overview.append(el("p", "Información solicitada: " + entry.requerimiento.detalle));
  if (entry.reapertura) overview.append(el("p", "Reapertura pendiente: " + entry.reapertura.motivo));
  content.append(overview);
  if (entry.cierres.length || entry.documentos.length) {
    const results = card("Respuestas y documentos");
    for (const closure of entry.cierres) {
      results.append(el("p", dateText(closure.fecha) + " · " + closure.resultado),
        el("p", closure.respuesta, { class: "detail-text" }));
    }
    for (const document of entry.documentos) results.append(button(document.nombre, async () => {
      const blob = await api(path + "/documentos/" + document.id);
      const url = URL.createObjectURL(blob);
      const a = el("a", null, { href: url, download: document.nombre });
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }));
    content.append(results);
  }
  if (entry.acciones.length) content.append(await caseActions(entry, path, openComplement));
  const timeline = card("Historial");
  const list = el("ol", null, { class: "history" });
  timeline.append(list);
  content.append(timeline);
  function add(events) {
    for (const item of events) list.append(el("li", dateText(item.fecha) + " · " + item.tipo +
      " · " + item.autor + (item.motivo ? " · " + item.motivo : "")));
  }
  add(history);
  if (history.length === 50) {
    const more = button("Cargar más movimientos", async () => {
      const events = await api(path + "/historial?offset=" + list.children.length);
      add(events);
      if (events.length < 50) more.remove();
    });
    timeline.append(more);
  }
}

async function caseActions(entry, path, openComplement) {
  const panel = card("Acciones disponibles");
  const reason = field("motivo", "Motivo", "textarea");
  const pdf = field("pdf", "Archivo PDF", "file", { optional: true });
  const staff = entry.acciones.some(key => ["asignacion", "resolver"].includes(key)) ?
    await api("/personal") : [];
  const person = field("responsable", "Responsable", "select", {
    options: staff.map(user => [user.id, user.nombre]), numeric: true,
  });
  const evaluation = [
    field("decision", "Decisión", "select", { options: [
      ["aceptar", "Aceptar"], ["requerir", "Pedir información"], ["rechazar", "Rechazar"],
    ] }), { ...reason, optional: true },
    field("tipo", "Tipo de complemento", "select", { options: options(["texto", "documento"]), optional: true }),
  ];
  if (entry.servicio === "Otro servicio") {
    evaluation.push(serviceField(true, catalog.filter(item => item.nombre !== "Otro servicio")));
  }
  const isCertificate = entry.servicio === "Expedición de certificados";
  const definitions = {
    corregir: ["Corregir solicitud", submission(entry), path, "PATCH"],
    cancelar: ["Cancelar solicitud", []],
    revision: ["Iniciar revisión", []],
    evaluacion: ["Evaluar solicitud", evaluation],
    complementos: ["Responder requerimiento", entry.requerimiento?.tipo === "documento" ?
      [{ ...pdf, optional: false }, field("texto", "Nota", "textarea", { optional: true })] :
      [field("texto", "Respuesta", "textarea")]],
    asignacion: ["Asignar responsable", [person]],
    finalizacion: ["Finalizar atención", [field("respuesta", "Respuesta", "textarea"),
      field("resultado", "Resultado", "select", { options: isCertificate ?
        [["expedido", "Certificado expedido"], ["no_expedido", "Certificado no expedido"]] :
        [["resuelto", "Resuelto"], ["no_resuelto", "No resuelto"]] }), pdf]],
    reaperturas: ["Solicitar reapertura", [reason]],
    resolver: ["Resolver reapertura", [field("decision", "Decisión", "select",
      { options: options(["aprobar", "rechazar"]) }), reason, { ...person, optional: true }],
      "/reaperturas/" + entry.reapertura?.id, "PATCH"],
    duplicado: ["Cerrar por duplicado", [field("principal", "Radicado principal"), reason]],
  };
  for (const key of entry.acciones) {
    const [title, fields, endpoint = path + "/" + key, method = "POST"] = definitions[key];
    const details = el("details");
    if (openComplement && key === "complementos") details.open = true;
    details.append(el("summary", title), buildForm(fields, title, async values => {
      const data = { ...values, version: entry.version };
      if (key === "complementos") data.requerimiento = entry.requerimiento.id;
      let body = data;
      if (["complementos", "finalizacion"].includes(key)) {
        body = new FormData();
        for (const [name, value] of Object.entries(data)) body.append(name, value);
      }
      await api(endpoint, method, body);
      await render();
      message("Cambio guardado.");
    }));
    panel.append(details);
  }
  return panel;
}

async function internal(supervision) {
  heading(supervision ? "Supervisión" : "Bandeja de atención");
  const filters = [
    field("estado", "Estado", "select", { options: options(states), optional: true }),
    serviceField(true),
  ];
  if (supervision) {
    const staff = await api("/personal");
    filters.push(field("responsable", "Responsable", "select", {
      options: staff.map(user => [user.id, user.nombre]), numeric: true, optional: true,
    }), field("prioridad", "Prioridad", "select", { options: options(["Baja", "Normal", "Alta"]), optional: true }),
    field("fecha", "Filtrar por", "select", { options: [["creada", "Radicación"], ["cerrada", "Cierre"]] }),
    field("desde", "Desde", "date", { optional: true }), field("hasta", "Hasta", "date", { optional: true }));
  }
  const target = el("div");
  const path = supervision ? "/supervision" : "/bandeja";
  content.append(buildForm(filters, "Aplicar filtros", values => listing(path, target, values, supervision),
    "filters"), target);
  await listing(path, target, {}, supervision);
}

function coordination() {
  heading("Administración");
  const staff = card("Alta de personal");
  staff.append(buildForm([...makeAccount, field("rol", "Roles", "select", { options: [
    ["atencion", "Atención"], ["coordinacion", "Coordinación"], ["atencion,coordinacion", "Atención y coordinación"],
    ["atencion,solicitante", "Atención y solicitante"],
    ["coordinacion,solicitante", "Coordinación y solicitante"],
    ["atencion,coordinacion,solicitante", "Los tres roles"],
  ] })], "Crear cuenta", async ({ rol, ...values }) => {
    await api("/personal", "POST", { ...values, roles: rol.split(",") });
    staff.querySelector("form").reset();
    message("Cuenta de personal creada.");
  }));
  const policy = card("Prioridades y plazos");
  policy.append(buildForm([serviceField(false, catalog.filter(item => item.nombre !== "Otro servicio")),
    field("prioridad", "Prioridad", "select", { options: options(["Normal", "Baja", "Alta"]) }),
    field("dias", "Días hábiles", "number", { min: 1 })], "Guardar política",
  async ({ servicio_id, ...values }) => {
    await api("/servicios/" + servicio_id, "PATCH", values);
    catalog = await api("/servicios");
    message("Política guardada para nuevas solicitudes.");
  }));
  content.append(staff, policy);
}

async function notices() {
  heading("Avisos");
  const panel = el("div");
  content.append(panel);
  async function page(offset) {
    const entries = await api("/avisos?limite=20&offset=" + offset);
    panel.replaceChildren();
    if (!entries.length) panel.append(el("p", "No hay avisos para mostrar."));
    for (const entry of entries) {
      const section = card(entry.tipo);
      section.append(el("p", dateText(entry.fecha)), caseLink(entry), " ",
        entry.leido ? "Leído" : button("Marcar como leído", async () => {
          await api("/avisos/" + entry.id, "PATCH");
          await page(offset);
        }));
      panel.append(section);
    }
    if (offset) panel.append(button("Anterior", () => page(offset - 20)));
    if (entries.length === 20) panel.append(button("Siguiente", () => page(offset + 20)));
  }
  await page(0);
}

async function render() {
  message("");
  if (!session) { access(); return; }
  nav.hidden = false;
  nav.replaceChildren();
  const roles = session.roles;
  const isStaff = roles.includes("atencion") || roles.includes("coordinacion");
  if (roles.includes("solicitante")) nav.append(link("Mis solicitudes", "mis-solicitudes"));
  if (isStaff) nav.append(link("Bandeja", "bandeja"));
  if (roles.includes("coordinacion")) {
    nav.append(link("Supervisión", "supervision"), link("Administración", "administracion"));
  }
  nav.append(link("Avisos", "avisos"));
  profile.hidden = false;
  profile.textContent = session.nombre || "Mi cuenta";
  sessionActions.replaceChildren(button("Salir", () => {
    session = null;
    catalog = [];
    sessionStorage.removeItem("radivela-session");
    location.hash = "";
    access();
  }));
  content.replaceChildren();
  try {
    message("Cargando…");
    if (!catalog.length) catalog = await api("/servicios");
    const route = location.hash.slice(1) || (roles.includes("solicitante") ? "mis-solicitudes" : "bandeja");
    const icons = { "mis-solicitudes": "▤", bandeja: "▤", supervision: "▥",
      administracion: "⚙", avisos: "♧" };
    const active = route.startsWith("caso/") || route === "nueva" ?
      (roles.includes("solicitante") ? "mis-solicitudes" : "bandeja") : route;
    for (const item of nav.querySelectorAll("a")) {
      const page = item.hash.slice(1);
      item.prepend(el("span", icons[page] || "", { class: "nav-icon", "aria-hidden": "true" }));
      if (page === active) item.setAttribute("aria-current", "page");
    }
    if (route.startsWith("caso/")) {
      const [, radicado, action] = route.split("/");
      await caseView(radicado, action === "complemento");
    }
    else if (route === "nueva") newCase();
    else if (route === "avisos") await notices();
    else if (route === "administracion") coordination();
    else if (route === "bandeja" || route === "supervision") await internal(route === "supervision");
    else await own();
    message("");
  } catch (error) {
    message(error.message, true);
  }
}

window.addEventListener("hashchange", render);
render();
