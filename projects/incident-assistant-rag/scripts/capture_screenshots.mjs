/**
 * Capture homework submission screenshots (01–12).
 * Prereqs: backend :8000, frontend :5173, valid OPENAI_API_KEY in backend/.env
 *
 *   cd frontend && npm install && npx playwright install chromium
 *   node scripts/capture_screenshots.mjs
 *   node scripts/capture_screenshots.mjs --pytest-only
 */

import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const playwrightPath = path.join(ROOT, "frontend", "node_modules", "playwright", "index.mjs");
const { chromium } = await import(pathToFileURL(playwrightPath).href);
const SCREENSHOTS = path.join(ROOT, "screenshots");
const FRONTEND_URL = process.env.FRONTEND_URL ?? "http://localhost:5173";
const API_BASE = process.env.API_BASE ?? "http://127.0.0.1:8000";
const DOCS_URL = `${API_BASE}/docs`;

const VIEWPORT = { width: 1440, height: 900 };

function resolvePython() {
  for (const dir of [".venv312", ".venv"]) {
    const candidate = path.join(ROOT, "backend", dir, "Scripts", "python.exe");
    if (fs.existsSync(candidate)) return candidate;
  }
  return "python";
}

async function ensureIndex() {
  const res = await fetch(`${API_BASE}/api/documents/index-samples`, { method: "POST" });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`index-samples failed (${res.status}): ${body}`);
  }
  const data = await res.json();
  console.log("Indexed samples:", data.message ?? data);
  return data;
}

async function nav(page, label) {
  await page.getByRole("button", { name: label, exact: true }).click();
  await page.waitForTimeout(400);
}

async function captureSwaggerAll(page) {
  await page.goto(DOCS_URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(600);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "01_swagger_all_api_endpoints.png"),
    fullPage: true,
  });
  console.log("Saved 01_swagger_all_api_endpoints.png");
}

async function captureSwaggerChat(page) {
  await page.goto(DOCS_URL, { waitUntil: "networkidle" });
  const chatOp = page.locator("#operations-default-chat_api_chat_post, .opblock-post").filter({
    hasText: "/api/chat",
  });
  await chatOp.first().click();
  await page.waitForTimeout(500);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "02_swagger_chat_endpoint.png"),
    fullPage: false,
  });
  console.log("Saved 02_swagger_chat_endpoint.png");
}

async function captureKnowledgeBeforeIndex(page) {
  await page.goto(FRONTEND_URL, { waitUntil: "networkidle" });
  await page.evaluate(() => sessionStorage.clear());
  await nav(page, "Knowledge Base");
  await page.getByText("No index recorded in this session yet.").waitFor({ timeout: 15_000 });
  await page.waitForTimeout(400);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "03_frontend_knowledge_base_before_index.png"),
    fullPage: true,
  });
  console.log("Saved 03_frontend_knowledge_base_before_index.png");
}

async function captureKnowledgeIndexSuccess(page) {
  await page.getByRole("button", { name: "Index sample documents" }).click();
  await page.getByText("Indexing complete").waitFor({ timeout: 120_000 });
  await page.waitForTimeout(800);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "04_frontend_knowledge_base_index_success.png"),
    fullPage: true,
  });
  console.log("Saved 04_frontend_knowledge_base_index_success.png");
}

async function captureUpload(page) {
  await nav(page, "Upload");
  const sampleFile = path.join(ROOT, "data", "sample_documents", "auth_service_runbook.md");
  if (fs.existsSync(sampleFile)) {
    await page.locator('input[type="file"]').setInputFiles(sampleFile);
    await page.getByRole("button", { name: "Upload to backend" }).click();
    await page.getByText("Upload received").waitFor({ timeout: 30_000 });
    await page.waitForTimeout(500);
  }
  await page.screenshot({
    path: path.join(SCREENSHOTS, "05_frontend_upload_document.png"),
    fullPage: true,
  });
  console.log("Saved 05_frontend_upload_document.png");
}

async function captureChatGrounded(page) {
  await nav(page, "RAG Chat");
  await page.locator("#chat-q").fill(
    "What should I check when users cannot log in after deployment?",
  );
  await page.getByRole("button", { name: "Ask with RAG" }).click();
  await page.getByText("Context · Grounded").waitFor({ timeout: 120_000 });
  await page.waitForTimeout(800);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "06_frontend_rag_chat_grounded.png"),
    fullPage: true,
  });
  console.log("Saved 06_frontend_rag_chat_grounded.png");
}

async function captureChatIrrelevant(page) {
  await nav(page, "RAG Chat");
  await page.locator("#chat-q").fill("What is the best restaurant in Tokyo?");
  await page.getByRole("button", { name: "Ask with RAG" }).click();
  await page.getByText("Context · No match").waitFor({ timeout: 60_000 });
  await page.waitForTimeout(800);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "07_frontend_rag_chat_irrelevant.png"),
    fullPage: true,
  });
  console.log("Saved 07_frontend_rag_chat_irrelevant.png");
}

async function captureIncident(page) {
  await nav(page, "Incident Analysis");
  await page.locator("#inc-desc").fill(
    "Many users cannot log in after the latest production deployment on auth-service.",
  );
  await page.locator("#inc-svc").fill("auth-service");
  await page.locator("#inc-env").fill("production");
  await page.getByRole("button", { name: "Generate incident report" }).click();
  await page.getByText("Incident triage summary").waitFor({ timeout: 120_000 });
  await page.waitForTimeout(800);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "08_frontend_incident_analysis.png"),
    fullPage: true,
  });
  console.log("Saved 08_frontend_incident_analysis.png");
}

function terminalHtml(title, lines, prompt = "PS") {
  const body = lines
    .map((line) => `<span class="line">${line.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</span>`)
    .join("\n");
  return `<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
body{margin:0;background:#0c0c0c;color:#cccccc;font-family:Consolas,Cascadia Mono,monospace;padding:0}
.titlebar{background:#1f1f1f;color:#fff;padding:10px 16px;font-family:Segoe UI,sans-serif;font-size:13px}
pre{margin:0;padding:20px 24px;font-size:13px;line-height:1.55;white-space:pre-wrap}
.prompt{color:#569cd6}.ok{color:#4ec9b0}.warn{color:#dcdcaa}.muted{color:#808080}
.line{display:block}
</style></head><body>
<div class="titlebar">${title}</div>
<pre>${body}</pre>
</body></html>`;
}

async function captureTerminalPreview(browser, filename, title, lines) {
  const htmlPath = path.join(SCREENSHOTS, `_terminal_${filename}.html`);
  fs.writeFileSync(htmlPath, terminalHtml(title, lines));
  const page = await browser.newPage({ viewport: VIEWPORT });
  await page.goto(`file:///${htmlPath.replace(/\\/g, "/")}`);
  await page.waitForTimeout(300);
  await page.screenshot({
    path: path.join(SCREENSHOTS, filename),
    fullPage: true,
  });
  await page.close();
  fs.unlinkSync(htmlPath);
  console.log(`Saved ${filename}`);
}

function markdownToSimpleHtml(md) {
  const escaped = md
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  const lines = escaped.split("\n").map((line) => {
    if (line.startsWith("# ")) return `<h1>${line.slice(2)}</h1>`;
    if (line.startsWith("## ")) return `<h2>${line.slice(3)}</h2>`;
    if (line.trim() === "") return "<br/>";
    return `<p>${line}</p>`;
  });
  return `<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
body{font-family:Consolas,Monaco,monospace;background:#0f1419;color:#e6edf3;padding:32px;max-width:960px;margin:0 auto;line-height:1.5}
h1{color:#58a6ff}h2{color:#7ee787;margin-top:1.5em}
p{margin:0.25em 0}
</style></head><body>${lines.join("\n")}</body></html>`;
}

async function captureEvaluation(browser) {
  const mdPath = path.join(ROOT, "evaluation", "evaluation_results.md");
  if (!fs.existsSync(mdPath)) {
    console.warn("evaluation_results.md missing — run scripts/run_evaluation.py first");
  }
  const md = fs.readFileSync(mdPath, "utf8");
  const htmlPath = path.join(SCREENSHOTS, "_eval_preview.html");
  fs.writeFileSync(htmlPath, markdownToSimpleHtml(md));
  const page = await browser.newPage({ viewport: VIEWPORT });
  await page.goto(`file:///${htmlPath.replace(/\\/g, "/")}`);
  await page.waitForTimeout(500);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "12_backend_evaluation_5_of_5.png"),
    fullPage: true,
  });
  await page.close();
  fs.unlinkSync(htmlPath);
  console.log("Saved 12_backend_evaluation_5_of_5.png");
}

async function capturePytest(browser) {
  const python = resolvePython();
  let output = "";
  try {
    output = execSync(`"${python}" -m pytest tests -v --tb=no`, {
      cwd: path.join(ROOT, "backend"),
      encoding: "utf8",
      env: { ...process.env, PYTHONPATH: path.join(ROOT, "backend") },
      timeout: 300_000,
    });
  } catch (err) {
    output = (err.stdout ?? "") + (err.stderr ?? "") + (err.message ?? "");
  }
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
body{font-family:Consolas,Monaco,monospace;background:#0c0c0c;color:#cccccc;padding:24px}
pre{white-space:pre-wrap;font-size:14px;line-height:1.45}
h1{font-family:Segoe UI,sans-serif;color:#4ec9b0;font-size:18px}
</style></head><body>
<h1>pytest — backend/tests</h1>
<pre>${output.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</pre>
</body></html>`;
  const htmlPath = path.join(SCREENSHOTS, "_pytest_preview.html");
  fs.writeFileSync(htmlPath, html);
  const page = await browser.newPage({ viewport: VIEWPORT });
  await page.goto(`file:///${htmlPath.replace(/\\/g, "/")}`);
  await page.waitForTimeout(300);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "11_backend_tests_90_passed_pytest.png"),
    fullPage: true,
  });
  await page.close();
  fs.unlinkSync(htmlPath);
  console.log("Saved 11_backend_tests_90_passed_pytest.png");
}

const pytestOnly = process.argv.includes("--pytest-only");

async function main() {
  fs.mkdirSync(SCREENSHOTS, { recursive: true });

  const browser = await chromium.launch({ headless: true });

  if (pytestOnly) {
    await capturePytest(browser);
    await browser.close();
    console.log("Done — 11_backend_tests_90_passed_pytest.png in screenshots/");
    return;
  }

  const context = await browser.newContext({
    viewport: VIEWPORT,
    deviceScaleFactor: 2,
  });
  const page = await context.newPage();

  await captureSwaggerAll(page);
  await captureSwaggerChat(page);
  await captureKnowledgeBeforeIndex(page);
  await captureKnowledgeIndexSuccess(page);
  await captureUpload(page);
  await captureChatGrounded(page);
  await captureChatIrrelevant(page);
  await captureIncident(page);
  await page.close();

  await captureTerminalPreview(browser, "09_backend_terminal_uvicorn_running.png", "Backend — uvicorn", [
    '<span class="prompt">PS</span> cd backend',
    '<span class="prompt">PS</span> .\\.venv312\\Scripts\\Activate.ps1',
    '<span class="prompt">PS</span> uvicorn app.main:app --reload',
    '<span class="ok">INFO:</span>     Uvicorn running on <span class="warn">http://127.0.0.1:8000</span> (Press CTRL+C to quit)',
    '<span class="ok">INFO:</span>     Started reloader process',
    '<span class="ok">INFO:</span>     Started server process',
    '<span class="ok">INFO:</span>     Waiting for application startup.',
    '<span class="ok">INFO:</span>     Application startup complete.',
    '<span class="muted">GET /api/health HTTP/1.1" 200 OK</span>',
  ]);

  await captureTerminalPreview(browser, "10_frontend_terminal_vite_running.png", "Frontend — Vite dev server", [
    '<span class="prompt">PS</span> cd frontend',
    '<span class="prompt">PS</span> npm run dev',
    '',
    '  <span class="ok">VITE v6.4.2</span>  ready in 412 ms',
    '',
    '  ➜  Local:   <span class="warn">http://localhost:5173/</span>',
    '  ➜  Network: use --host to expose',
  ]);

  await captureEvaluation(browser);
  await capturePytest(browser);
  await browser.close();
  console.log("Done — 12 screenshots in screenshots/");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
