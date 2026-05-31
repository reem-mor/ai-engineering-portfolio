/**
 * Capture submission screenshots for incident-rag-bedrock.
 *
 * Prereqs:
 *   docker compose up --build -d   → http://localhost:8080
 *   py -3.12 scripts/kb_smoke_test.py   → evaluation/smoke_results.md
 *
 *   cd scripts && npm install && npx playwright install chromium
 *   node capture_screenshots.mjs
 *   node capture_screenshots.mjs --pytest-only
 */

import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const playwrightPath = path.join(__dirname, "node_modules", "playwright", "index.mjs");
const { chromium } = await import(pathToFileURL(playwrightPath).href);
const SCREENSHOTS = path.join(ROOT, "screenshots");
const APP_URL = process.env.APP_URL ?? "http://localhost:8080";
const VIEWPORT = { width: 1440, height: 900 };

function resolvePython312() {
  try {
    execSync("py -3.12 --version", { stdio: "pipe" });
    return "py -3.12";
  } catch {
    return "python";
  }
}

function markdownToSimpleHtml(md) {
  const escaped = md
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  const lines = escaped.split("\n").map((line) => {
    if (line.startsWith("# ")) return `<h1>${line.slice(2)}</h1>`;
    if (line.startsWith("## ")) return `<h2>${line.slice(3)}</h2>`;
    if (line.startsWith("|")) return `<p class="table">${line}</p>`;
    if (line.trim() === "") return "<br/>";
    return `<p>${line}</p>`;
  });
  return `<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
body{font-family:Consolas,Monaco,monospace;background:#0f1419;color:#e6edf3;padding:32px;max-width:960px;margin:0 auto;line-height:1.5}
h1{color:#58a6ff}h2{color:#7ee787;margin-top:1.5em}
p{margin:0.25em 0}.table{font-size:12px;color:#c9d1d9}
</style></head><body>${lines.join("\n")}</body></html>`;
}

async function waitForHtmx(page) {
  await page.waitForFunction(() => typeof htmx !== "undefined", undefined, { timeout: 15_000 });
}

async function captureHomepage(page) {
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await waitForHtmx(page);
  await page.waitForSelector(".topnav", { timeout: 15_000 });
  await page.waitForSelector("#ask-form", { timeout: 15_000 });
  await page.waitForTimeout(500);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "07_app_homepage_public.png"),
    fullPage: true,
  });
  console.log("Saved 07_app_homepage_public.png");
}

async function submitQuestion(page, question) {
  await page.locator("#live-kb").scrollIntoViewIfNeeded();
  await page.locator("#question").fill(question);
  const [response] = await Promise.all([
    page.waitForResponse(
      (r) => r.url().includes("/ask") && r.request().method() === "POST",
      { timeout: 120_000 },
    ),
    page.locator("#submit-btn").click(),
  ]);
  if (!response.ok()) {
    throw new Error(`/ask failed with HTTP ${response.status()}`);
  }
}

async function captureGroundedAnswer(page) {
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await waitForHtmx(page);
  await submitQuestion(page, "How do I triage an authentication service incident?");
  await page.locator("#answer .badge-grounded").waitFor({ timeout: 5_000 });
  await page.locator("#answer .citation-list").waitFor({ timeout: 5_000 });
  await page.waitForTimeout(800);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "08_app_question_and_answer.png"),
    fullPage: false,
  });
  console.log("Saved 08_app_question_and_answer.png (Live KB + citation labels)");
}

async function captureRefusal(page) {
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await waitForHtmx(page);
  await submitQuestion(page, "What is the best restaurant in Tokyo?");
  await page.locator("#answer .badge-nomatch").waitFor({ timeout: 5_000 });
  await page.waitForTimeout(800);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "09_app_refusal_or_low_confidence.png"),
    fullPage: false,
  });
  console.log("Saved 09_app_refusal_or_low_confidence.png");
}

async function captureMvpWorkflow(page) {
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await waitForHtmx(page);
  await page.locator("#mvp").scrollIntoViewIfNeeded();
  const [response] = await Promise.all([
    page.waitForResponse(
      (r) => r.url().includes("/workflow/triage") && r.request().method() === "POST",
      { timeout: 120_000 },
    ),
    page.locator("#workflow-submit").click(),
  ]);
  if (!response.ok()) {
    throw new Error(`/workflow/triage failed with HTTP ${response.status()}`);
  }
  await page.locator("#workflow-result .workflow-result").waitFor({ timeout: 5_000 });
  await page.waitForTimeout(800);
  await page.locator("#mvp").screenshot({
    path: path.join(SCREENSHOTS, "13_mvp_workflow.png"),
  });
  console.log("Saved 13_mvp_workflow.png");
}

async function captureArchitecture(page) {
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await waitForHtmx(page);
  await page.locator("#architecture").scrollIntoViewIfNeeded();
  await page.locator('[data-arch-block="documents"]').click();
  await page.waitForTimeout(400);
  await page.locator("#architecture").screenshot({
    path: path.join(SCREENSHOTS, "14_architecture.png"),
  });
  console.log("Saved 14_architecture.png");
}

async function capturePytest(browser) {
  const python = resolvePython312();
  let output = "";
  try {
    output = execSync(`${python} -m pytest -v --tb=no`, {
      cwd: ROOT,
      encoding: "utf8",
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
<h1>pytest — incident-rag-bedrock</h1>
<pre>${output.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</pre>
</body></html>`;
  const htmlPath = path.join(SCREENSHOTS, "_pytest_preview.html");
  fs.writeFileSync(htmlPath, html);
  const page = await browser.newPage({ viewport: VIEWPORT });
  await page.goto(`file:///${htmlPath.replace(/\\/g, "/")}`);
  await page.waitForTimeout(300);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "11_pytest_43_passed.png"),
    fullPage: true,
  });
  await page.close();
  fs.unlinkSync(htmlPath);
  console.log("Saved 11_pytest_43_passed.png");
}

async function captureSmokeResults(browser) {
  const mdPath = path.join(ROOT, "evaluation", "smoke_results.md");
  if (!fs.existsSync(mdPath)) {
    throw new Error("evaluation/smoke_results.md missing — run scripts/kb_smoke_test.py first");
  }
  const md = fs.readFileSync(mdPath, "utf8");
  const htmlPath = path.join(SCREENSHOTS, "_smoke_preview.html");
  fs.writeFileSync(htmlPath, markdownToSimpleHtml(md));
  const page = await browser.newPage({ viewport: VIEWPORT });
  await page.goto(`file:///${htmlPath.replace(/\\/g, "/")}`);
  await page.waitForTimeout(500);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "12_kb_smoke_evaluation.png"),
    fullPage: true,
  });
  await page.close();
  fs.unlinkSync(htmlPath);
  console.log("Saved 12_kb_smoke_evaluation.png");
}

const pytestOnly = process.argv.includes("--pytest-only");

async function main() {
  fs.mkdirSync(SCREENSHOTS, { recursive: true });
  const browser = await chromium.launch({ headless: true });

  if (pytestOnly) {
    await capturePytest(browser);
    await browser.close();
    console.log("Done — 11_pytest_43_passed.png");
    return;
  }

  const context = await browser.newContext({
    viewport: VIEWPORT,
    deviceScaleFactor: 2,
  });
  const page = await context.newPage();

  await captureHomepage(page);
  await captureGroundedAnswer(page);
  await captureRefusal(page);
  await captureMvpWorkflow(page);
  await captureArchitecture(page);
  await page.close();

  await capturePytest(browser);
  await captureSmokeResults(browser);
  await browser.close();
  console.log("Done — screenshots 07–09, 11–14 in screenshots/");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
