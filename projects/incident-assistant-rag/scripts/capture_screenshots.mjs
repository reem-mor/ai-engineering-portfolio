/**
 * Capture homework submission screenshots (06, 07, 08, 11, 12).
 * Prereqs: backend :8000, frontend :5173, valid OPENAI_API_KEY in backend/.env
 *
 *   cd frontend && npm install -D playwright && npx playwright install chromium
 *   node scripts/capture_screenshots.mjs
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

const VIEWPORT = { width: 1440, height: 900 };

async function ensureIndex() {
  const res = await fetch(`${API_BASE}/api/documents/index-samples`, { method: "POST" });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`index-samples failed (${res.status}): ${body}`);
  }
  const data = await res.json();
  console.log("Indexed samples:", data.message ?? data);
}

async function nav(page, label) {
  await page.getByRole("button", { name: label, exact: true }).click();
  await page.waitForTimeout(400);
}

async function captureChatGrounded(page) {
  await nav(page, "RAG Chat");
  await page.locator("#chat-q").fill(
    "What should I check when users cannot log in after deployment?",
  );
  await page.getByRole("button", { name: "Send to model" }).click();
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
  await page.getByRole("button", { name: "Send to model" }).click();
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
  await page.getByText("Severity ·").waitFor({ timeout: 120_000 });
  await page.waitForTimeout(800);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "08_frontend_incident_analysis.png"),
    fullPage: true,
  });
  console.log("Saved 08_frontend_incident_analysis.png");
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
  const venvPython = path.join(ROOT, "backend", ".venv", "Scripts", "python.exe");
  const python = fs.existsSync(venvPython) ? venvPython : "python";
  let output = "";
  try {
    output = execSync(`"${python}" -m pytest tests -q`, {
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

async function main() {
  fs.mkdirSync(SCREENSHOTS, { recursive: true });
  console.log("Ensuring FAISS index from sample documents...");
  await ensureIndex();

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: VIEWPORT,
    deviceScaleFactor: 2,
  });
  const page = await context.newPage();

  await page.goto(FRONTEND_URL, { waitUntil: "networkidle" });
  await captureChatGrounded(page);
  await captureChatIrrelevant(page);
  await captureIncident(page);
  await page.close();

  await captureEvaluation(browser);
  await capturePytest(browser);
  await browser.close();
  console.log("Done.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
