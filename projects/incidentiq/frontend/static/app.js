/**
 * IncidentIQ — frontend controller.
 * Vanilla JS, ES2022. No build step, no dependencies.
 * All listeners bound in JS; no inline handlers. No inline styles.
 */
"use strict";

// ─── CONFIG ───────────────────────────────────────────────────────────────
const API_BASE = window.location.origin;
const MAX_QUESTION_LENGTH = 500;
const MIN_QUESTION_LENGTH = 3;
const CHAR_WARN = 400;
const CHAR_CRIT = 480;
const MAX_RECENT_QUERIES = 5;
const RECENT_QUERIES_KEY = "iiq.recent.v1";
const STATS_REFRESH_MS = 60_000;
const HEALTH_REFRESH_MS = 30_000;
const ERROR_AUTODISMISS_MS = 5_000;
const SOURCE_PREVIEW_CHARS = 300;
const VIEWPORT_DESKTOP = 1024;

// ─── PRESETS (6 real corpus scenarios — ids match sample_incidents.py) ───
const PRESETS = Object.freeze([
  {
    docType: "incident",
    docId: "INC-006",
    severity: "P1",
    text: "What are the triage steps for a P1 Kubernetes pod crash loop?",
    icon: kubernetesIcon(),
  },
  {
    docType: "incident",
    docId: "INC-001",
    severity: "P1",
    text: "How do I resolve PostgreSQL connection pool exhaustion?",
    icon: dbIcon(),
  },
  {
    docType: "sop",
    docId: "SOP-MQ-001",
    severity: "P1",
    text: "What is the SOP for Kafka consumer lag incidents?",
    icon: queueIcon(),
  },
  {
    docType: "incident",
    docId: "INC-016",
    severity: "P1",
    text: "We are seeing 5xx errors spiking on our API gateway, what do I do?",
    icon: networkIcon(),
  },
  {
    docType: "incident",
    docId: "INC-027",
    severity: "P2",
    text: "How do I handle a GCP IAM permission denied error in CI/CD?",
    icon: cloudIcon(),
  },
  {
    docType: "incident",
    docId: "INC-012",
    severity: "P1",
    text: "How do I troubleshoot internal DNS resolution failures?",
    icon: networkIcon(),
  },
]);

// ─── APM / VENDORS (static) ───────────────────────────────────────────────
const APM_TOOLS = Object.freeze([
  { group: "Monitoring", items: [
    { letter: "D", name: "Datadog",     desc: "APM, Infrastructure, Logs" },
    { letter: "N", name: "New Relic",   desc: "APM, Browser, Synthetics" },
    { letter: "G", name: "Grafana",     desc: "Metrics, Dashboards" },
    { letter: "P", name: "Prometheus",  desc: "Metrics collection" },
  ]},
  { group: "Incident Management", items: [
    { letter: "P", name: "PagerDuty",   desc: "On-call, Escalation" },
    { letter: "O", name: "OpsGenie",    desc: "Alerting, On-call" },
    { letter: "S", name: "StatusPage",  desc: "Communication" },
  ]},
  { group: "Cloud Consoles", items: [
    { letter: "A", name: "AWS Console", desc: "Amazon Web Services" },
    { letter: "G", name: "GCP Console", desc: "Google Cloud Platform" },
    { letter: "A", name: "Azure Portal",desc: "Microsoft Azure" },
  ]},
]);

const IMPACT_KAFKA = Object.freeze([
  { dot: "🔴", name: "payment-events",     desc: "Revenue impact" },
  { dot: "🔴", name: "order-processing",   desc: "Order impact" },
  { dot: "🟠", name: "inventory-updates",  desc: "Stock impact" },
  { dot: "🟡", name: "notification-events",desc: "Alert impact" },
  { dot: "🟡", name: "audit-log",          desc: "Compliance impact" },
]);

const IMPACT_DISKS = Object.freeze([
  { dot: "🔴", name: "/var/lib/etcd",          desc: "K8s cluster state" },
  { dot: "🔴", name: "PostgreSQL WAL dir",     desc: "DB writes" },
  { dot: "🟠", name: "/var/kafka-logs",        desc: "Queue data" },
  { dot: "🟠", name: "MySQL binlog dir",       desc: "DB replication" },
  { dot: "🟡", name: "/var/log",               desc: "Log accumulation" },
]);

const ESCALATION = Object.freeze([
  { cat: "P1 Database",    team: "DBA On-Call Team",         askCat: "Database" },
  { cat: "P1 Kubernetes",  team: "Platform Engineering",     askCat: "Kubernetes" },
  { cat: "P1 Network",     team: "Network Operations",       askCat: "Network" },
  { cat: "P1 Application", team: "App Team Lead",            askCat: "Application" },
  { cat: "P1 Cloud",       team: "Cloud Infrastructure",     askCat: "Cloud" },
  { cat: "All P1",         team: "Engineering Manager",      askCat: "any" },
]);

// ─── STATE ────────────────────────────────────────────────────────────────
const state = {
  severityFilter: "All",
  isLoading: false,
  currentAbort: null,
  recentQueries: [],
  timer: { seconds: 0, running: false, intervalId: null, resolvedAt: null },
  statsTimer: null,
  healthTimer: null,
  errorTimer: null,
  lastResponse: null,
  health: null,
  queryCancelled: false,
  queryGeneration: 0,
  activeTab: "search",
  stats: null,
  incidents: null,
  sops: null,
  resources: null,
  incidentsExpanded: false,
  modalResourceRef: null,
  modalContext: null,
  detailCache: new Map(),
  recentIncidents: [],
};

// ─── DOM REFS ─────────────────────────────────────────────────────────────
const el = {};
function $(id) {
  const node = document.getElementById(id);
  if (!node) throw new Error(`Missing DOM node: #${id}`);
  return node;
}
function cacheDom() {
  const ids = [
    "layout","status-dot","p1-incident-count",
    "stats-list","sop-browser","incident-browser","incident-show-more",
    "resource-list","apm-tools",
    "severity-chips","chip-count-all","chip-count-p1","chip-count-p2","chip-count-p3",
    "query-form","query-input","char-count","char-counter","submit-btn","clear-btn",
    "print-btn","copy-summary-btn",
    "presets-section","preset-grid",
    "latest-incidents-section","latest-incidents-list",
    "loading-panel","loading-vector-count","cancel-btn",
    "error-banner","error-message","info-banner","info-message",
    "answer-panel","confidence-badge","answer-stats",
    "copy-answer-btn","print-answer-btn","clear-answer-btn",
    "p1-alert","answer-body","mttr-estimate","mttr-estimate-value",
    "sources-toggle","sources-count","sources-list",
    "timer-display","timer-resolved",
    "timer-start","timer-pause","timer-resolve","timer-reset",
    "recent-queries","recent-clear-btn",
    "impact-kafka","impact-disks","escalation-list",
    "bottom-nav",
    "modal-backdrop","modal-title","modal-body","modal-close","modal-ask-btn",
    "toast",
  ];
  ids.forEach((id) => { el[id] = $(id); });
}

// ─── UTILS ────────────────────────────────────────────────────────────────
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
function clamp(n, lo, hi) { return Math.max(lo, Math.min(hi, n)); }
function truncate(s, n) { return String(s).length <= n ? String(s) : String(s).slice(0, n - 1) + "…"; }
function formatHHMMSS(secs) {
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  const s = secs % 60;
  return `${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
}
function formatSecs(ms) {
  if (typeof ms !== "number" || Number.isNaN(ms)) return "—";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}
function timeAgo(ts) {
  const diff = Math.max(0, Date.now() - ts);
  const s = Math.floor(diff / 1000);
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  return `${h}h ago`;
}

// ─── ICONS (inline SVG) ───────────────────────────────────────────────────
function kubernetesIcon() {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2 3 7v10l9 5 9-5V7l-9-5z"/><path d="M12 12v10M3 7l9 5 9-5"/></svg>`;
}
function dbIcon() {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v6c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 11v6c0 1.66 4 3 9 3s9-1.34 9-3v-6"/></svg>`;
}
function queueIcon() {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="6" width="6" height="12" rx="1"/><rect x="11" y="6" width="6" height="12" rx="1"/><path d="M19 9v6"/></svg>`;
}
function networkIcon() {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/></svg>`;
}
function cloudIcon() {
  return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>`;
}

// ─── API CALLS ────────────────────────────────────────────────────────────
async function apiGet(path, signal) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: { Accept: "application/json" },
    signal,
  });
  if (!res.ok) throw new Error(`GET ${path} failed: HTTP ${res.status}`);
  return res.json();
}

async function loadBootstrap() {
  try {
    const data = await apiGet("/api/bootstrap");
    state.stats = data.stats;
    state.incidents = data.incidents;
    state.sops = data.sops;
    state.resources = data.resources;
    state.recentIncidents = data.recent_incidents || [];
    renderStats(data.stats);
    renderSeverityChipCounts(data.stats);
    el["loading-vector-count"].textContent = String(data.stats?.total_vectors ?? 64);
    renderSOPBrowser(data.sops);
    renderIncidentBrowser(data.incidents);
    renderResources(data.resources);
    renderLatestIncidents(state.recentIncidents);
  } catch (err) {
    console.warn("[IncidentIQ] bootstrap fetch failed, falling back to individual endpoints:", err);
    await loadStats();
    await Promise.all([loadSOPs(), loadIncidents(), loadResources()]);
  }
}

async function loadStats() {
  try {
    const data = await apiGet("/api/stats");
    state.stats = data;
    renderStats(data);
    renderSeverityChipCounts(data);
    el["loading-vector-count"].textContent = String(data.total_vectors ?? 64);
  } catch (err) {
    console.warn("[IncidentIQ] stats fetch failed:", err);
  }
}

async function loadSOPs() {
  try {
    state.sops = await apiGet("/api/sops");
    renderSOPBrowser(state.sops);
  } catch (err) {
    console.warn("[IncidentIQ] sops fetch failed:", err);
    el["sop-browser"].innerHTML = `<p class="browse-empty">SOPs unavailable.</p>`;
  }
}

async function loadIncidents() {
  try {
    state.incidents = await apiGet("/api/incidents");
    renderIncidentBrowser(state.incidents);
  } catch (err) {
    console.warn("[IncidentIQ] incidents fetch failed:", err);
    el["incident-browser"].innerHTML = `<p class="browse-empty">Incidents unavailable.</p>`;
  }
}

async function loadResources() {
  try {
    state.resources = await apiGet("/api/resources");
    renderResources(state.resources);
  } catch (err) {
    console.warn("[IncidentIQ] resources fetch failed:", err);
    el["resource-list"].innerHTML = `<p class="browse-empty">Resources unavailable.</p>`;
  }
}

async function probeHealth() {
  try {
    const body = await apiGet("/health");
    state.health = body;
    const ok = body?.status === "healthy" && body?.faiss_index_loaded;
    setStatusDot(ok ? "healthy" : "degraded");
    return body;
  } catch {
    state.health = null;
    setStatusDot("degraded");
    return null;
  }
}

async function showHealthDetails() {
  const body = state.health ?? await probeHealth();
  if (!body) {
    showError("Cannot reach backend. Check that the server is running.");
    return;
  }
  const lines = [
    `Status: ${body.status}`,
    `FAISS index: ${body.faiss_index_loaded ? "loaded" : "not loaded"}`,
    `Documents indexed: ${body.total_documents_indexed ?? "—"}`,
    `LLM: ${body.llm_model ?? "—"}`,
    `Version: ${body.version ?? "—"}`,
  ];
  showInfo(lines.join(" · "), true);
}

function setStatusDot(kind) {
  const dot = el["status-dot"];
  dot.classList.remove("status-dot--healthy","status-dot--degraded","status-dot--unknown");
  dot.classList.add(`status-dot--${kind}`);
  const label = kind === "healthy" ? "All systems operational"
              : kind === "degraded" ? "Backend degraded or unreachable"
              : "Checking system status";
  dot.title = `${label} — click for details`;
  dot.setAttribute("aria-label", `${label} — click for details`);
}

async function callQuery(question, severityFilter) {
  if (state.currentAbort) state.currentAbort.abort();
  const ac = new AbortController();
  state.currentAbort = ac;

  const payload = { question };
  if (severityFilter && severityFilter !== "All") payload.severity_filter = severityFilter;

  const res = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(payload),
    signal: ac.signal,
  });

  let body = null;
  try { body = await res.json(); } catch { /* tolerate empty */ }

  if (!res.ok) {
    const err = new Error(`HTTP ${res.status}`);
    err.status = res.status;
    err.body = body;
    throw err;
  }
  return body;
}

// ─── RENDER: STATS ────────────────────────────────────────────────────────
function renderStats(stats) {
  const list = el["stats-list"];
  list.innerHTML = "";
  const rows = [
    `<li class="stats-row">🔴 P1: <strong>${stats.p1_incidents}</strong> incidents</li>`,
    `<li class="stats-row">🟠 P2: <strong>${stats.p2_incidents}</strong> incidents</li>`,
    `<li class="stats-row">🟡 P3: <strong>${stats.p3_incidents}</strong> incidents</li>`,
    `<li class="stats-row">📚 <strong>${stats.total_sops}</strong> SOPs indexed</li>`,
    `<li class="stats-row">📄 <strong>${stats.file_documents_indexed || 0}</strong> file documents</li>`,
    `<li class="stats-row">⚡ Avg P1 MTTR: <strong>${stats.avg_mttr_p1_minutes} min</strong></li>`,
    `<li class="stats-row">🧠 <strong>${stats.total_vectors}</strong> vectors indexed</li>`,
  ];
  list.innerHTML = rows.join("");
  updateHeaderP1Count(stats);
}

function updateHeaderP1Count(stats) {
  el["p1-incident-count"].textContent = String(stats?.p1_incidents ?? 0);
}

function renderSeverityChipCounts(stats) {
  const total = (stats.p1_incidents || 0) + (stats.p2_incidents || 0) + (stats.p3_incidents || 0);
  el["chip-count-all"].textContent = String(total);
  el["chip-count-p1"].textContent = String(stats.p1_incidents || 0);
  el["chip-count-p2"].textContent = String(stats.p2_incidents || 0);
  el["chip-count-p3"].textContent = String(stats.p3_incidents || 0);
}

// ─── RENDER: SOP BROWSER ─────────────────────────────────────────────────
function renderSOPBrowser(sops) {
  const root = el["sop-browser"];
  root.innerHTML = "";
  if (!Array.isArray(sops) || sops.length === 0) {
    root.innerHTML = `<p class="browse-empty">No SOPs available.</p>`;
    return;
  }
  const groups = { P1: [], P2: [], P3: [], OTHER: [] };
  sops.forEach((sop) => {
    const k = ["P1","P2","P3"].includes(sop.severity_trigger) ? sop.severity_trigger : "OTHER";
    groups[k].push(sop);
  });
  const frag = document.createDocumentFragment();
  ["P1","P2","P3","OTHER"].forEach((sev) => {
    if (groups[sev].length === 0) return;
    const title = document.createElement("div");
    title.className = "browse-group-title";
    title.textContent = sev === "OTHER" ? "Other" : `${sev} Trigger`;
    frag.appendChild(title);
    groups[sev].forEach((sop) => frag.appendChild(makeSOPRow(sop)));
  });
  root.appendChild(frag);
}

function makeSOPRow(sop) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "browse-item is-sop";
  btn.dataset.sopId = sop.id;
  btn.innerHTML = `
    <div class="browse-item-row">
      <span class="severity-badge is-${(sop.severity_trigger || "na").toLowerCase()}">${escapeHtml(sop.severity_trigger || "N/A")}</span>
      <span class="browse-item-title">${escapeHtml(sop.title)}</span>
    </div>
    <div class="browse-item-meta">
      <span class="pill-mini">${escapeHtml(sop.id)}</span>
      <span>${escapeHtml(sop.owner)}</span>
    </div>
  `;
  btn.addEventListener("click", () => {
    document.querySelectorAll(".browse-item.is-sop.is-active").forEach((n) => n.classList.remove("is-active"));
    btn.classList.add("is-active");
    void openKnowledgeModal("sop", sop.id);
  });
  return btn;
}

// ─── RENDER: INCIDENT BROWSER ─────────────────────────────────────────────
function renderIncidentBrowser(grouped) {
  const root = el["incident-browser"];
  root.innerHTML = "";
  const all = ["P1","P2","P3"];
  const frag = document.createDocumentFragment();
  const limit = state.incidentsExpanded ? Infinity : 5;
  let totalShown = 0;
  let totalAvailable = 0;

  all.forEach((sev) => {
    const items = grouped[sev] || [];
    totalAvailable += items.length;
    if (items.length === 0) return;
    const title = document.createElement("div");
    title.className = "browse-group-title";
    title.textContent = `${sev} (${items.length})`;
    frag.appendChild(title);
    items.slice(0, limit).forEach((inc) => {
      frag.appendChild(makeIncidentRow(inc, sev));
      totalShown++;
    });
  });

  root.appendChild(frag);
  const allShown = totalShown >= totalAvailable;
  el["incident-show-more"].hidden = allShown;
  el["incident-show-more"].textContent = state.incidentsExpanded ? "Show fewer" : "Show all incidents";
}

function makeIncidentRow(inc, sev) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = `browse-item is-${sev.toLowerCase()}`;
  btn.innerHTML = `
    <div class="browse-item-row">
      <span class="severity-badge is-${sev.toLowerCase()}">${sev}</span>
      <span class="browse-item-title">${escapeHtml(truncate(inc.title, 35))}</span>
    </div>
    <div class="browse-item-meta">
      <span class="pill-mini">${escapeHtml(inc.id)}</span>
      <span>⏱ ${inc.mttr_minutes}min</span>
    </div>
  `;
  btn.addEventListener("click", () => {
    void openKnowledgeModal("incident", inc.id);
  });
  return btn;
}

// ─── RENDER: RESOURCES ────────────────────────────────────────────────────
function renderResources(resources) {
  const root = el["resource-list"];
  root.innerHTML = "";
  if (!Array.isArray(resources) || resources.length === 0) {
    root.innerHTML = `<p class="browse-empty">No resources available.</p>`;
    return;
  }
  const frag = document.createDocumentFragment();
  resources.forEach((ref) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "browse-item is-ref";
    btn.innerHTML = `
      <div class="browse-item-row">
        <span class="severity-badge is-ref">${escapeHtml(ref.category || "REF")}</span>
        <span class="browse-item-title">${escapeHtml(ref.title)}</span>
      </div>
      <div class="browse-item-meta">
        <span>${escapeHtml(ref.mttr_impact || "—")}</span>
      </div>
      <div class="browse-item-tags">
        ${(ref.key_concepts || []).slice(0, 3).map((c) => `<span class="tag-mini">${escapeHtml(c)}</span>`).join("")}
      </div>
    `;
    btn.addEventListener("click", () => openResourceModal(ref));
    frag.appendChild(btn);
  });
  root.appendChild(frag);
}

// ─── RENDER: APM TOOLS ────────────────────────────────────────────────────
function renderAPMTools() {
  const root = el["apm-tools"];
  root.innerHTML = "";
  const frag = document.createDocumentFragment();
  APM_TOOLS.forEach((group) => {
    const t = document.createElement("div");
    t.className = "apm-group-title";
    t.textContent = group.group;
    frag.appendChild(t);
    group.items.forEach((item) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "apm-pill";
      btn.title = item.desc;
      btn.innerHTML = `
        <span class="apm-letter" aria-hidden="true">${escapeHtml(item.letter)}</span>
        <span class="apm-name">${escapeHtml(item.name)}</span>
      `;
      btn.addEventListener("click", () => {
        populateAndSubmit(`How do I use ${item.name} for incident response?`);
      });
      frag.appendChild(btn);
    });
  });
  root.appendChild(frag);
}

// ─── RENDER: BUSINESS IMPACT ──────────────────────────────────────────────
function renderImpact() {
  const k = el["impact-kafka"];
  const d = el["impact-disks"];
  k.innerHTML = "";
  d.innerHTML = "";
  IMPACT_KAFKA.forEach((row) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "impact-item";
    btn.innerHTML = `<span class="impact-dot" aria-hidden="true">${row.dot}</span><span><strong>${escapeHtml(row.name)}</strong> · ${escapeHtml(row.desc)}</span>`;
    btn.addEventListener("click", () => {
      populateAndSubmit(`What should I do if ${row.name} is having issues?`);
    });
    li.appendChild(btn);
    k.appendChild(li);
  });
  IMPACT_DISKS.forEach((row) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "impact-item";
    btn.innerHTML = `<span class="impact-dot" aria-hidden="true">${row.dot}</span><span><strong>${escapeHtml(row.name)}</strong> · ${escapeHtml(row.desc)}</span>`;
    btn.addEventListener("click", () => {
      populateAndSubmit(`What should I do if ${row.name} is having issues?`);
    });
    li.appendChild(btn);
    d.appendChild(li);
  });
}

// ─── RENDER: ESCALATION ───────────────────────────────────────────────────
function renderEscalation() {
  const root = el["escalation-list"];
  root.innerHTML = "";
  ESCALATION.forEach((row) => {
    const li = document.createElement("li");
    li.className = "escalation-row";
    li.innerHTML = `
      <div class="escalation-cat">${escapeHtml(row.cat)}</div>
      <div class="escalation-team">${escapeHtml(row.team)}</div>
    `;
    const ask = document.createElement("button");
    ask.type = "button";
    ask.className = "escalation-ask";
    ask.textContent = "Ask IC";
    ask.addEventListener("click", () => {
      const cat = row.askCat === "any" ? "P1" : `${row.askCat} P1`;
      populateAndSubmit(`What is the escalation process for ${cat} incidents?`);
    });
    li.appendChild(ask);
    root.appendChild(li);
  });
}

// ─── PRESETS ──────────────────────────────────────────────────────────────
function renderPresets() {
  const root = el["preset-grid"];
  root.innerHTML = "";
  const frag = document.createDocumentFragment();
  PRESETS.forEach((p, idx) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "preset-btn";
    btn.dataset.idx = String(idx);
    btn.innerHTML = `
      <span class="preset-icon" aria-hidden="true">${p.icon}</span>
      <span class="preset-text">${escapeHtml(p.text)}</span>
      <span class="preset-sev"><span class="severity-badge is-${p.severity.toLowerCase()}">${p.severity}</span></span>
    `;
    btn.addEventListener("click", () => handlePresetClick(btn, p));
    frag.appendChild(btn);
  });
  root.appendChild(frag);
}

function handlePresetClick(btn, preset) {
  document.querySelectorAll(".preset-btn.is-clicked").forEach((n) => n.classList.remove("is-clicked"));
  btn.classList.add("is-clicked");
  window.setTimeout(() => btn.classList.remove("is-clicked"), 200);
  void openKnowledgeModal(preset.docType, preset.docId, preset.text);
}

function renderLatestIncidents(rows) {
  const section = el["latest-incidents-section"];
  const root = el["latest-incidents-list"];
  root.innerHTML = "";
  if (!Array.isArray(rows) || rows.length === 0) {
    section.hidden = true;
    return;
  }
  section.hidden = false;
  const frag = document.createDocumentFragment();
  rows.forEach((inc) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "latest-incident-btn";
    btn.innerHTML = `
      <span class="severity-badge is-${(inc.severity || "p3").toLowerCase()}">${escapeHtml(inc.severity || "P3")}</span>
      <span class="latest-incident-text">
        <span class="latest-incident-id">${escapeHtml(inc.id)}</span>
        <span class="latest-incident-title">${escapeHtml(truncate(inc.title, 52))}</span>
      </span>
      <span class="latest-incident-meta">⏱ ${inc.mttr_minutes}m · ${escapeHtml(inc.category || "")}</span>
    `;
    btn.addEventListener("click", () => {
      void openKnowledgeModal("incident", inc.id);
    });
    frag.appendChild(btn);
  });
  root.appendChild(frag);
}

async function fetchKnowledgeDetail(type, id) {
  const cacheKey = `${type}:${id}`;
  if (state.detailCache.has(cacheKey)) {
    return state.detailCache.get(cacheKey);
  }
  const path = type === "sop" ? `/api/sops/${encodeURIComponent(id)}` : `/api/incidents/${encodeURIComponent(id)}`;
  const detail = await apiGet(path);
  state.detailCache.set(cacheKey, detail);
  return detail;
}

function renderListSection(title, items) {
  if (!Array.isArray(items) || items.length === 0) return "";
  const lis = items.map((item, idx) => `<li><span class="detail-step-num">${idx + 1}.</span> ${escapeHtml(String(item))}</li>`).join("");
  return `<section class="detail-block"><h4>${escapeHtml(title)}</h4><ol class="detail-list">${lis}</ol></section>`;
}

function renderIncidentDetailHtml(inc) {
  return `
    <div class="detail-meta">
      <span class="severity-badge is-${(inc.severity || "p3").toLowerCase()}">${escapeHtml(inc.severity)}</span>
      <span class="pill-mini">${escapeHtml(inc.id)}</span>
      <span class="pill-mini">${escapeHtml(inc.category)}</span>
      <span class="pill-mini">⏱ ${inc.mttr_minutes} min MTTR</span>
      ${inc.sop_reference ? `<span class="pill-mini">SOP: ${escapeHtml(inc.sop_reference)}</span>` : ""}
    </div>
    <section class="detail-block"><h4>Description</h4><p>${escapeHtml(inc.description)}</p></section>
    ${renderListSection("Triage Steps", inc.triage_steps)}
    <section class="detail-block"><h4>Root Cause</h4><p>${escapeHtml(inc.root_cause)}</p></section>
    ${renderListSection("Resolution Steps", inc.resolution_steps)}
    ${inc.lessons_learned ? `<section class="detail-block"><h4>Lessons Learned</h4><p>${escapeHtml(inc.lessons_learned)}</p></section>` : ""}
  `;
}

function renderSOPDetailHtml(sop) {
  return `
    <div class="detail-meta">
      <span class="severity-badge is-${(sop.severity_trigger || "na").toLowerCase()}">${escapeHtml(sop.severity_trigger)}</span>
      <span class="pill-mini">${escapeHtml(sop.id)}</span>
      <span class="pill-mini">v${escapeHtml(sop.version || "1.0")}</span>
      <span class="pill-mini">${escapeHtml(sop.owner)}</span>
    </div>
    <section class="detail-block"><h4>Applicability</h4><p>${escapeHtml(sop.applicability)}</p></section>
    ${renderListSection("Runbook Steps", sop.steps)}
    ${sop.escalation_path ? `<section class="detail-block"><h4>Escalation</h4><p>${escapeHtml(sop.escalation_path)}</p></section>` : ""}
  `;
}

async function openKnowledgeModal(type, id, suggestedQuery) {
  try {
    const detail = await fetchKnowledgeDetail(type, id);
    const title = detail.title || id;
    const askQuery = suggestedQuery
      || (type === "sop"
        ? `What is the SOP for ${title}?`
        : `How do I resolve ${id} ${title}?`);
    state.modalResourceRef = null;
    state.modalContext = { type, id, askQuery, title };
    el["modal-title"].textContent = `${id} — ${title}`;
    el["modal-body"].innerHTML = type === "sop"
      ? renderSOPDetailHtml(detail)
      : renderIncidentDetailHtml(detail);
    el["modal-ask-btn"].textContent = "Ask IncidentIQ about this";
    el["modal-backdrop"].hidden = false;
    if (window.innerWidth < VIEWPORT_DESKTOP) setActiveTab("search");
  } catch (err) {
    console.warn("[IncidentIQ] detail fetch failed:", err);
    showError(`Could not load ${type} ${id}. Please try again.`);
  }
}

// ─── SEVERITY CHIPS ───────────────────────────────────────────────────────
function wireSeverityChips() {
  const chips = el["severity-chips"].querySelectorAll(".chip");
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      if (state.isLoading) return;
      const sev = chip.dataset.severity || "All";
      state.severityFilter = sev;
      chips.forEach((c) => {
        const active = c === chip;
        c.classList.toggle("is-active", active);
        c.setAttribute("aria-checked", active ? "true" : "false");
      });
    });
  });
}

// ─── CHAR COUNT / SUBMIT STATE ────────────────────────────────────────────
function updateCharCount() {
  const len = el["query-input"].value.length;
  el["char-count"].textContent = String(len);
  const c = el["char-counter"];
  c.classList.toggle("is-warning",  len >= CHAR_WARN && len < CHAR_CRIT);
  c.classList.toggle("is-critical", len >= CHAR_CRIT);
}

function updateSubmitState() {
  const t = el["query-input"].value.trim();
  const valid = t.length >= MIN_QUESTION_LENGTH && t.length <= MAX_QUESTION_LENGTH && !state.isLoading;
  el["submit-btn"].disabled = !valid;
}

function updateClearVisibility() {
  const hasInput = el["query-input"].value.length > 0;
  const hasAnswer = !el["answer-panel"].hidden;
  el["clear-btn"].hidden = !(hasInput || hasAnswer);
  el["print-btn"].hidden = !hasAnswer;
  el["copy-summary-btn"].hidden = !hasAnswer;
}

function autoExpandTextarea() {
  const ta = el["query-input"];
  ta.style.height = "auto";
  const lineH = 24;
  const min = lineH * 3 + 16;
  const max = lineH * 6 + 16;
  ta.style.height = `${clamp(ta.scrollHeight, min, max)}px`;
}

// ─── BANNERS ──────────────────────────────────────────────────────────────
function showError(msg, autoDismiss = true) {
  el["error-message"].textContent = msg;
  el["error-banner"].hidden = false;
  el["info-banner"].hidden = true;
  if (state.errorTimer) window.clearTimeout(state.errorTimer);
  if (autoDismiss) {
    state.errorTimer = window.setTimeout(() => { el["error-banner"].hidden = true; }, ERROR_AUTODISMISS_MS);
  }
}
function showInfo(msg, autoDismiss = false) {
  el["info-message"].textContent = msg;
  el["info-banner"].hidden = false;
  el["error-banner"].hidden = true;
  if (autoDismiss) {
    window.setTimeout(() => { el["info-banner"].hidden = true; }, ERROR_AUTODISMISS_MS);
  }
}
function hideBanners() {
  el["error-banner"].hidden = true;
  el["info-banner"].hidden = true;
}

// ─── LOADING STATE ────────────────────────────────────────────────────────
function setLoading(isLoading) {
  state.isLoading = isLoading;
  el["loading-panel"].hidden = !isLoading;
  el["presets-section"].hidden = isLoading;
  el["query-input"].disabled = isLoading;
  el["severity-chips"].querySelectorAll(".chip").forEach((c) => c.toggleAttribute("disabled", isLoading));

  if (isLoading) {
    el["submit-btn"].disabled = true;
  } else {
    updateSubmitState();
  }

  const steps = el["loading-panel"].querySelectorAll(".loading-step");
  steps.forEach((s) => s.classList.remove("is-active","is-done"));
  if (isLoading) {
    if (state._loadingTimers) state._loadingTimers.forEach((t) => clearTimeout(t));
    state._loadingTimers = [];
    steps[0]?.classList.add("is-active");
    state._loadingTimers.push(window.setTimeout(() => {
      steps[0]?.classList.remove("is-active");
      steps[0]?.classList.add("is-done");
      steps[1]?.classList.add("is-active");
    }, 1500));
    state._loadingTimers.push(window.setTimeout(() => {
      steps[1]?.classList.remove("is-active");
      steps[1]?.classList.add("is-done");
      steps[2]?.classList.add("is-active");
    }, 3000));
  } else {
    if (state._loadingTimers) state._loadingTimers.forEach((t) => clearTimeout(t));
    state._loadingTimers = [];
  }
}

// ─── SUBMIT FLOW ──────────────────────────────────────────────────────────
async function submitQuery() {
  const question = el["query-input"].value.trim();
  if (question.length < MIN_QUESTION_LENGTH) {
    showError(`Please enter at least ${MIN_QUESTION_LENGTH} characters.`);
    return;
  }
  if (question.length > MAX_QUESTION_LENGTH) {
    showError(`Question exceeds ${MAX_QUESTION_LENGTH} characters.`);
    return;
  }
  hideBanners();
  el["answer-panel"].hidden = true;
  state.queryCancelled = false;
  const generation = ++state.queryGeneration;
  setLoading(true);

  try {
    const data = await callQuery(question, state.severityFilter);
    if (generation !== state.queryGeneration) return;
    setLoading(false);
    state.lastResponse = data;
    saveRecentQuery(question, data?.confidence, Array.isArray(data?.sources) ? data.sources.length : 0);
    renderAnswer(data);
  } catch (err) {
    if (generation !== state.queryGeneration) return;
    setLoading(false);
    if (err?.name === "AbortError") {
      if (!state.queryCancelled) showInfo("Query cancelled.", true);
      return;
    }
    if (err?.status === 422) {
      showError("Question is too short or invalid. Please try again.");
    } else if (err?.status >= 500 || err?.status === 503) {
      showError("Server error. Please retry shortly.");
    } else if (err?.status) {
      showError(`Unexpected error (HTTP ${err.status}).`);
    } else {
      showError("Cannot connect to server. Make sure the backend is running.");
    }
  } finally {
    if (generation === state.queryGeneration) state.currentAbort = null;
  }
}

// ─── RENDER: ANSWER ───────────────────────────────────────────────────────
function renderAnswer(data) {
  hideBanners();
  const conf = data?.confidence || "none";
  const badge = el["confidence-badge"];
  badge.classList.remove("is-high","is-medium","is-low","is-none");
  badge.classList.add(`is-${conf}`);
  badge.textContent = conf.toUpperCase();

  const ms = Number(data?.processing_time_ms ?? 0);
  const sources = Array.isArray(data?.sources) ? data.sources : [];
  el["answer-stats"].textContent = `⚡ ${formatSecs(ms)} · ${sources.length} sources · ${data?.model_used || "—"}`;

  el["answer-body"].innerHTML = renderAnswerMarkdown(data?.answer ?? "");
  wireAnswerCopyButtons();

  const hasP1 = sources.some((s) => String(s.severity).toUpperCase() === "P1");
  el["p1-alert"].hidden = !hasP1;

  renderMttrEstimate(sources);
  renderSources(sources);

  el["answer-panel"].hidden = false;
  el["sources-toggle"].setAttribute("aria-expanded", window.innerWidth >= VIEWPORT_DESKTOP ? "true" : "false");
  el["sources-list"].hidden = !(window.innerWidth >= VIEWPORT_DESKTOP);
  updateClearVisibility();

  if (conf === "none") {
    showInfo(data?.answer || "No grounded answer was returned. Try rephrasing or escalate to your team lead.");
  }

  el["answer-panel"].scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderAnswerMarkdown(rawText) {
  const text = String(rawText || "").replace(/\r\n/g, "\n");
  const lines = text.split("\n");
  const sections = [];
  let currentHeading = null;
  let currentLines = [];

  const pushSection = () => {
    if (currentHeading === null && currentLines.length === 0) return;
    sections.push({ heading: currentHeading, lines: currentLines });
    currentLines = [];
  };

  for (const raw of lines) {
    const line = raw.trimEnd();
    if (/^##\s+/.test(line)) {
      pushSection();
      currentHeading = line.replace(/^##\s+/, "").trim();
    } else {
      currentLines.push(line);
    }
  }
  pushSection();

  const out = [];
  for (const sec of sections) {
    const isEscalation = (sec.heading || "").toLowerCase().includes("escalation");
    const isResolution = (sec.heading || "").toLowerCase().includes("resolution");
    const wrap = isEscalation ? "escalation-block" : null;
    const inner = [];

    if (sec.heading) inner.push(`<h3>${escapeHtml(sec.heading)}</h3>`);
    inner.push(renderSectionBody(sec.lines, isResolution));

    if (wrap) {
      out.push(`<div class="${wrap}">${inner.join("")}</div>`);
    } else {
      out.push(inner.join(""));
    }
  }
  return out.join("");
}

function renderSectionBody(lines, withCopy) {
  const out = [];
  let listBuf = [];
  const flushList = () => {
    if (listBuf.length === 0) return;
    const items = listBuf.map((line) => {
      const stripped = line.replace(/^\s*\d+\.\s+/, "");
      const inner = applyInline(escapeHtml(stripped));
      const copyBtn = withCopy ? `<button type="button" class="step-copy" data-step-text="${escapeHtml(stripped)}">Copy</button>` : "";
      return `<li>${inner}${copyBtn}</li>`;
    }).join("");
    out.push(`<ol>${items}</ol>`);
    listBuf = [];
  };

  for (const raw of lines) {
    const line = raw.trim();
    if (line === "") { flushList(); continue; }
    if (/^\s*\d+\.\s+/.test(raw)) { listBuf.push(raw); continue; }
    flushList();
    if (/^```/.test(line)) continue;
    out.push(`<p>${applyInline(escapeHtml(line))}</p>`);
  }
  flushList();
  return out.join("");
}

function applyInline(escaped) {
  let s = escaped;
  s = s.replace(/`([^`]+)`/g, (_m, p1) => `<code>${p1}</code>`);
  s = s.replace(/\*\*([^*]+)\*\*/g, (_m, p1) => `<strong>${p1}</strong>`);
  return s;
}

function wireAnswerCopyButtons() {
  el["answer-body"].querySelectorAll(".step-copy").forEach((btn) => {
    btn.addEventListener("click", async (ev) => {
      ev.stopPropagation();
      const txt = btn.dataset.stepText || btn.previousSibling?.textContent || "";
      const ok = await copyToClipboard(txt);
      if (ok) {
        btn.classList.add("is-copied");
        btn.textContent = "Copied";
        window.setTimeout(() => { btn.classList.remove("is-copied"); btn.textContent = "Copy"; }, 1500);
      }
    });
  });
}

function renderMttrEstimate(sources) {
  const mttrs = [];
  for (const s of sources) {
    const inc = (state.incidents?.[String(s.severity).toUpperCase()] || []).find((i) => i.id === s.id);
    if (inc?.mttr_minutes) mttrs.push(inc.mttr_minutes);
  }
  if (mttrs.length === 0) { el["mttr-estimate"].hidden = true; return; }
  const avg = Math.round(mttrs.reduce((a, b) => a + b, 0) / mttrs.length);
  el["mttr-estimate-value"].textContent = `~${avg} min`;
  el["mttr-estimate"].hidden = false;
}

function renderSources(sources) {
  el["sources-count"].textContent = String(sources.length);
  const list = el["sources-list"];
  list.innerHTML = "";
  if (sources.length === 0) return;

  const frag = document.createDocumentFragment();
  sources.forEach((src) => {
    const pct = clamp(Math.round((src.relevance_score ?? 0) * 100), 0, 100);
    const sev = String(src.severity || "N/A").toUpperCase();
    const dt = String(src.document_type || "").toLowerCase();
    const cls = sev === "P1" ? "is-p1" : sev === "P2" ? "is-p2" : sev === "P3" ? "is-p3"
              : dt === "sop" ? "is-sop" : dt === "reference" ? "is-ref" : "";
    const docLabel = dt === "sop" ? "SOP" : dt === "incident" ? "INC" : dt === "reference" ? "REF" : "—";
    const docClass = dt === "sop" ? "is-sop" : dt === "reference" ? "is-ref" : `is-${sev.toLowerCase()}`;

    const preview = truncate(String(src.chunk_text || ""), SOURCE_PREVIEW_CHARS) || "(no preview available)";
    const sourceFile = src.source_file ? `<span class="source-file">📎 ${escapeHtml(src.source_file)}</span>` : "";

    const li = document.createElement("li");
    li.className = `source-card ${cls}`;
    li.dataset.sourceId = src.id || "";
    li.innerHTML = `
      <div class="source-head">
        <div class="source-head-left">
          <div class="source-id-row">
            <span class="severity-badge ${docClass}">${docLabel}</span>
            <span>${escapeHtml(src.id || "—")}</span>
            <span>·</span>
            <span>${escapeHtml(src.category || "—")}</span>
            <span class="severity-badge is-${sev.toLowerCase()}">${escapeHtml(sev)}</span>
          </div>
          <h4 class="source-title">${escapeHtml(src.title || "Untitled")}</h4>
          ${sourceFile}
        </div>
        <div class="source-head-right">${pct}%</div>
      </div>
      <div class="relevance-bar"><span class="relevance-fill" data-target="${pct}"></span></div>
      <div class="source-body">${escapeHtml(preview)}</div>
      <div class="source-footer">
        <button type="button" class="source-ask-btn">Ask about this →</button>
      </div>
    `;
    li.querySelector(".source-head").addEventListener("click", () => toggleSourceExpand(li));
    li.querySelector(".source-ask-btn").addEventListener("click", (ev) => {
      ev.stopPropagation();
      const sid = String(src.id || "").toUpperCase();
      if (sid.startsWith("INC-")) {
        void openKnowledgeModal("incident", sid);
      } else if (sid.startsWith("SOP-")) {
        void openKnowledgeModal("sop", sid);
      } else {
        populateAndSubmit(`Tell me more about ${src.title}`);
      }
    });
    frag.appendChild(li);
  });
  list.appendChild(frag);

  window.requestAnimationFrame(() => {
    list.querySelectorAll(".relevance-fill").forEach((node) => {
      const target = Number(node.dataset.target || "0");
      node.style.transform = `scaleX(${target / 100})`;
    });
  });
}

function toggleSourceExpand(card) {
  card.classList.toggle("is-expanded");
}

// ─── ACTION BUTTONS ──────────────────────────────────────────────────────
function clearAll() {
  el["query-input"].value = "";
  el["query-input"].focus();
  el["answer-panel"].hidden = true;
  el["sources-list"].innerHTML = "";
  el["answer-body"].innerHTML = "";
  el["p1-alert"].hidden = true;
  el["mttr-estimate"].hidden = true;
  state.lastResponse = null;
  hideBanners();
  autoExpandTextarea();
  updateCharCount();
  updateSubmitState();
  updateClearVisibility();
}

async function copyAnswer() {
  const text = el["answer-body"].innerText.trim();
  if (!text) return;
  const ok = await copyToClipboard(text);
  if (ok) flashCopy(el["copy-answer-btn"]);
}

async function copySummary() {
  const r = state.lastResponse;
  if (!r) return;
  const sources = (r.sources || []).map((s) => `- [${s.severity}] ${s.id} ${s.title} (${Math.round((s.relevance_score || 0) * 100)}%)`).join("\n");
  const summary = [
    `IncidentIQ Summary`,
    `Question: ${r.query}`,
    `Confidence: ${String(r.confidence || "none").toUpperCase()}`,
    `Processing: ${formatSecs(r.processing_time_ms)}`,
    `Model: ${r.model_used}`,
    ``,
    `Sources (${(r.sources || []).length}):`,
    sources || "(none)",
    ``,
    `Answer:`,
    r.answer,
  ].join("\n");
  const ok = await copyToClipboard(summary);
  if (ok) flashCopy(el["copy-summary-btn"]);
}

function flashCopy(btn) {
  if (!btn) return;
  const original = btn.textContent;
  btn.classList.add("is-copied");
  btn.textContent = "Copied!";
  showToast("Copied to clipboard");
  window.setTimeout(() => {
    btn.classList.remove("is-copied");
    btn.textContent = original;
  }, 1500);
}

function printAnswer() {
  if (el["answer-panel"].hidden) return;
  window.print();
}

async function copyToClipboard(text) {
  try {
    if (navigator.clipboard && window.isSecureContext !== false) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch { /* fall through */ }
  try {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    document.body.removeChild(ta);
    return true;
  } catch (err) {
    console.error("[IncidentIQ] clipboard error:", err);
    showError("Could not copy to clipboard.");
    return false;
  }
}

// ─── TOAST ────────────────────────────────────────────────────────────────
let _toastTimer = null;
function showToast(msg) {
  const t = el["toast"];
  t.textContent = msg;
  t.hidden = false;
  if (_toastTimer) window.clearTimeout(_toastTimer);
  _toastTimer = window.setTimeout(() => { t.hidden = true; }, 1500);
}

// ─── INCIDENT TIMER ───────────────────────────────────────────────────────
function startTimer() {
  if (state.timer.running) return;
  state.timer.running = true;
  state.timer.resolvedAt = null;
  el["timer-resolved"].hidden = true;
  state.timer.intervalId = window.setInterval(() => {
    state.timer.seconds += 1;
    renderTimer();
  }, 1000);
  syncTimerButtons();
}
function pauseTimer() {
  if (!state.timer.running) return;
  state.timer.running = false;
  if (state.timer.intervalId) window.clearInterval(state.timer.intervalId);
  state.timer.intervalId = null;
  syncTimerButtons();
}
function resolveTimer() {
  pauseTimer();
  if (state.timer.seconds === 0) return;
  state.timer.resolvedAt = state.timer.seconds;
  el["timer-resolved"].hidden = false;
  el["timer-resolved"].innerHTML = `✅ Resolved in <strong>${formatHHMMSS(state.timer.seconds)}</strong> <button type="button" class="btn-mini" id="timer-resolved-copy">Copy</button>`;
  document.getElementById("timer-resolved-copy")?.addEventListener("click", () => {
    copyToClipboard(`Resolved in ${formatHHMMSS(state.timer.resolvedAt)}`).then((ok) => ok && showToast("Resolution time copied"));
  });
  syncTimerButtons();
}
function resetTimer() {
  pauseTimer();
  state.timer.seconds = 0;
  state.timer.resolvedAt = null;
  el["timer-resolved"].hidden = true;
  renderTimer();
  syncTimerButtons();
}
function renderTimer() {
  const t = el["timer-display"];
  t.textContent = formatHHMMSS(state.timer.seconds);
  t.classList.toggle("is-warning",  state.timer.seconds >= 900  && state.timer.seconds < 1800);
  t.classList.toggle("is-critical", state.timer.seconds >= 1800);
}
function syncTimerButtons() {
  el["timer-start"].disabled = state.timer.running;
  el["timer-pause"].disabled = !state.timer.running;
  el["timer-resolve"].disabled = state.timer.seconds === 0;
}

// ─── RECENT QUERIES (sessionStorage) ──────────────────────────────────────
function loadRecentQueries() {
  try {
    const raw = sessionStorage.getItem(RECENT_QUERIES_KEY);
    state.recentQueries = raw ? JSON.parse(raw) : [];
  } catch {
    state.recentQueries = [];
  }
  renderRecentQueries();
}
function saveRecentQuery(question, confidence, sourceCount) {
  const entry = { q: question, c: confidence || "none", n: sourceCount || 0, t: Date.now() };
  state.recentQueries = [entry, ...state.recentQueries.filter((r) => r.q !== question)].slice(0, MAX_RECENT_QUERIES);
  try { sessionStorage.setItem(RECENT_QUERIES_KEY, JSON.stringify(state.recentQueries)); } catch { /* ignore */ }
  renderRecentQueries();
}
function clearRecentQueries() {
  state.recentQueries = [];
  try { sessionStorage.removeItem(RECENT_QUERIES_KEY); } catch { /* ignore */ }
  renderRecentQueries();
}
function renderRecentQueries() {
  const list = el["recent-queries"];
  list.innerHTML = "";
  if (state.recentQueries.length === 0) {
    list.innerHTML = `<li class="recent-empty">No queries yet this session</li>`;
    return;
  }
  const frag = document.createDocumentFragment();
  state.recentQueries.forEach((r) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "recent-item";
    btn.innerHTML = `
      <span class="severity-badge is-${r.c}">${escapeHtml(String(r.c).toUpperCase())}</span>
      ${escapeHtml(truncate(r.q, 40))}
      <div class="recent-meta">
        <span>${escapeHtml(timeAgo(r.t))}</span>
        <span>·</span>
        <span>${r.n} sources</span>
      </div>
    `;
    btn.addEventListener("click", () => {
      el["query-input"].value = r.q;
      autoExpandTextarea();
      updateCharCount();
      updateSubmitState();
      submitQuery();
    });
    li.appendChild(btn);
    frag.appendChild(li);
  });
  list.appendChild(frag);
}

// ─── MODAL ────────────────────────────────────────────────────────────────
function openResourceModal(ref) {
  state.modalContext = {
    type: "resource",
    id: ref.id,
    askQuery: `Tell me more about ${ref.title}`,
    title: ref.title,
  };
  state.modalResourceRef = ref;
  el["modal-title"].textContent = ref.title || "Resource";
  el["modal-body"].textContent = ref.content || "(no content)";
  el["modal-ask-btn"].textContent = "Ask IncidentIQ about this";
  el["modal-backdrop"].hidden = false;
}
function closeModal() {
  el["modal-backdrop"].hidden = true;
  state.modalResourceRef = null;
  state.modalContext = null;
}

// ─── TABS (mobile) ────────────────────────────────────────────────────────
function setActiveTab(tab) {
  state.activeTab = tab;
  el["layout"].dataset.activeTab = tab;
  el["bottom-nav"].querySelectorAll(".bn-btn").forEach((b) => {
    b.classList.toggle("is-active", b.dataset.tab === tab);
  });
  if (tab === "resources") {
    window.requestAnimationFrame(() => {
      document.getElementById("key-resources-section")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }
}

function wireBottomNav() {
  el["bottom-nav"].querySelectorAll(".bn-btn").forEach((b) => {
    b.addEventListener("click", () => setActiveTab(b.dataset.tab || "search"));
  });
  setActiveTab("search");
}

// ─── POPULATE-AND-SUBMIT (used by sidebars, presets, escalations) ─────────
function populateAndSubmit(text) {
  el["query-input"].value = text;
  autoExpandTextarea();
  updateCharCount();
  updateSubmitState();
  updateClearVisibility();
  if (window.innerWidth < VIEWPORT_DESKTOP) setActiveTab("search");
  submitQuery();
}

// ─── WIRING ───────────────────────────────────────────────────────────────
function wireEvents() {
  el["query-input"].addEventListener("input", () => {
    updateCharCount();
    updateSubmitState();
    updateClearVisibility();
    autoExpandTextarea();
  });

  el["query-input"].addEventListener("keydown", (ev) => {
    if ((ev.ctrlKey || ev.metaKey) && ev.key === "Enter") {
      ev.preventDefault();
      if (!el["submit-btn"].disabled) submitQuery();
    } else if (ev.key === "Escape") {
      ev.preventDefault();
      clearAll();
    }
  });

  el["query-form"].addEventListener("submit", (ev) => {
    ev.preventDefault();
    submitQuery();
  });

  el["clear-btn"].addEventListener("click", clearAll);
  el["clear-answer-btn"].addEventListener("click", clearAll);
  el["print-btn"].addEventListener("click", printAnswer);
  el["print-answer-btn"].addEventListener("click", printAnswer);
  el["copy-summary-btn"].addEventListener("click", copySummary);
  el["copy-answer-btn"].addEventListener("click", copyAnswer);

  el["cancel-btn"].addEventListener("click", () => {
    if (!state.currentAbort && !state.isLoading) return;
    state.queryCancelled = true;
    state.queryGeneration += 1;
    state.currentAbort?.abort();
    state.currentAbort = null;
    setLoading(false);
    showInfo("Query cancelled.", true);
  });

  el["status-dot"].addEventListener("click", () => { void showHealthDetails(); });

  el["sources-toggle"].addEventListener("click", () => {
    const expanded = el["sources-toggle"].getAttribute("aria-expanded") === "true";
    el["sources-toggle"].setAttribute("aria-expanded", expanded ? "false" : "true");
    el["sources-list"].hidden = expanded;
  });

  el["timer-start"].addEventListener("click", startTimer);
  el["timer-pause"].addEventListener("click", pauseTimer);
  el["timer-resolve"].addEventListener("click", resolveTimer);
  el["timer-reset"].addEventListener("click", resetTimer);

  el["recent-clear-btn"].addEventListener("click", clearRecentQueries);

  el["modal-close"].addEventListener("click", closeModal);
  el["modal-ask-btn"].addEventListener("click", () => {
    const ctx = state.modalContext;
    if (!ctx?.askQuery) return;
    closeModal();
    populateAndSubmit(ctx.askQuery);
  });
  el["modal-backdrop"].addEventListener("click", (ev) => {
    if (ev.target === el["modal-backdrop"]) closeModal();
  });
  document.addEventListener("keydown", (ev) => {
    if (ev.key === "Escape" && !el["modal-backdrop"].hidden) closeModal();
  });

  el["incident-show-more"].addEventListener("click", () => {
    state.incidentsExpanded = !state.incidentsExpanded;
    if (state.incidents) renderIncidentBrowser(state.incidents);
  });
}

// ─── INIT ─────────────────────────────────────────────────────────────────
async function init() {
  cacheDom();
  renderPresets();
  renderAPMTools();
  renderImpact();
  renderEscalation();
  loadRecentQueries();
  wireSeverityChips();
  wireBottomNav();
  wireEvents();
  autoExpandTextarea();
  updateCharCount();
  updateSubmitState();
  updateClearVisibility();
  renderTimer();
  syncTimerButtons();

  await loadBootstrap();
  await probeHealth();

  state.statsTimer  = window.setInterval(loadStats, STATS_REFRESH_MS);
  state.healthTimer = window.setInterval(probeHealth, HEALTH_REFRESH_MS);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
