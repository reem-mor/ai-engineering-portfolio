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
 *   node capture_screenshots.mjs --mvp-only   → 13_mvp_workflow.png only
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
    if (line.startsWith("### ")) return `<h3>${line.slice(4)}</h3>`;
    if (line.startsWith("|")) return `<p class="table">${line}</p>`;
    if (line.trim() === "---") return `<hr class="divider"/>`;
    if (line.trim() === "") return "<br/>";
    if (line.startsWith("- ")) return `<p class="bullet">${line}</p>`;
    if (line.startsWith("**")) return `<p class="strong">${line}</p>`;
    return `<p>${line}</p>`;
  });
  return `<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
body{font-family:Segoe UI,Consolas,Monaco,monospace;background:#0f1419;color:#e6edf3;padding:32px;max-width:980px;margin:0 auto;line-height:1.5}
h1{color:#58a6ff;font-size:22px}h2{color:#7ee787;margin-top:1.25em;font-size:17px}h3{color:#d2a8ff;font-size:14px}
p{margin:0.25em 0}.table{font-size:12px;color:#c9d1d9;font-family:Consolas,Monaco,monospace}
.bullet{margin-left:0.5em;color:#c9d1d9}.strong{color:#f0f6fc}.divider{border:none;border-top:1px solid #30363d;margin:1em 0}
.meta{color:#8b949e;font-size:13px;margin-bottom:1em}
</style></head><body>${lines.join("\n")}</body></html>`;
}

function extractCorpusMarkdown() {
  const readmePath = path.join(ROOT, "data", "sample_documents", "README.md");
  const raw = fs.readFileSync(readmePath, "utf8");
  const start = raw.indexOf("## Format coverage");
  const end = raw.indexOf("## Out-of-corpus questions");
  if (start === -1 || end === -1) {
    throw new Error("Could not slice corpus tables from data/sample_documents/README.md");
  }
  const s3 =
    "s3://reem-amdocs-ai-artifacts-3331/projects/incident-rag-bedrock/data/sample_documents/";
  return `# Knowledge Base Corpus — Incident Operations

- **S3 prefix:** \`${s3}\`
- **Documents:** 10 files across MD, TXT, CSV, DOCX, PDF

${raw.slice(start, end).trim()}
`;
}

async function screenshotMarkdownFile(browser, mdPath, outputName, missingMessage) {
  if (!fs.existsSync(mdPath)) {
    throw new Error(missingMessage);
  }
  const md = fs.readFileSync(mdPath, "utf8");
  const htmlPath = path.join(SCREENSHOTS, `_preview_${outputName}.html`);
  fs.writeFileSync(htmlPath, markdownToSimpleHtml(md));
  const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });
  await page.goto(`file:///${htmlPath.replace(/\\/g, "/")}`);
  await page.waitForTimeout(500);
  await page.screenshot({
    path: path.join(SCREENSHOTS, outputName),
    fullPage: true,
  });
  await page.close();
  fs.unlinkSync(htmlPath);
  console.log(`Saved ${outputName}`);
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

function unionBoundingBoxes(...boxes) {
  const valid = boxes.filter(Boolean);
  if (valid.length === 0) throw new Error("No bounding boxes to union");
  const x = Math.min(...valid.map((b) => b.x));
  const y = Math.min(...valid.map((b) => b.y));
  const right = Math.max(...valid.map((b) => b.x + b.width));
  const bottom = Math.max(...valid.map((b) => b.y + b.height));
  return {
    x: Math.floor(x),
    y: Math.floor(y),
    width: Math.ceil(right - x),
    height: Math.ceil(bottom - y),
  };
}

async function captureMvpWorkflow(page) {
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await page.locator("#mvp").scrollIntoViewIfNeeded();
  const [response] = await Promise.all([
    page.waitForResponse(
      (r) =>
        r.url().includes("/workflow/triage") && r.request().method() === "POST",
      { timeout: 120_000 },
    ),
    page.getByRole("button", { name: /Run triage/i }).click(),
  ]);
  if (!response.ok()) {
    throw new Error(`/workflow/triage failed with HTTP ${response.status()}`);
  }
  await page.waitForFunction(
    () => {
      const mvp = document.querySelector("#mvp");
      if (!mvp) return false;
      return (
        /Recommended steps/i.test(mvp.textContent || "") ||
        mvp.querySelector("[data-step-badge]") !== null
      );
    },
    { timeout: 60_000 },
  );
  await page.waitForTimeout(800);

  const title = page.locator("#mvp h2");
  const grid = page.locator("#mvp div.mt-8.grid").first();
  await title.waitFor({ state: "visible" });
  await grid.waitFor({ state: "visible" });
  const titleBox = await title.boundingBox();
  const gridBox = await grid.boundingBox();
  const clip = unionBoundingBoxes(titleBox, gridBox);

  await page.screenshot({
    path: path.join(SCREENSHOTS, "13_mvp_workflow.png"),
    clip,
  });
  console.log(`Saved 13_mvp_workflow.png (${clip.width}x${clip.height} clip)`);
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

async function captureUploadSuccess(page) {
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await waitForHtmx(page);
  await page.locator("#document-upload").scrollIntoViewIfNeeded();
  const samplePath = path.join(ROOT, "data", "sample_documents", "api_gateway_5xx_runbook.txt");
  if (!fs.existsSync(samplePath)) {
    console.warn("Skipping 15 — sample txt missing");
    return;
  }
  await page.locator("#document").setInputFiles(samplePath);
  const [response] = await Promise.all([
    page.waitForResponse(
      (r) => r.url().includes("/documents/upload") && r.request().method() === "POST",
      { timeout: 120_000 },
    ),
    page.locator("#upload-submit").click(),
  ]);
  if (!response.ok()) {
    console.warn(`Skipping 15 — upload returned HTTP ${response.status()}`);
    return;
  }
  await page.locator("#upload-result .upload-result--success").waitFor({ timeout: 5_000 });
  await page.waitForTimeout(500);
  await page.locator("#document-upload").screenshot({
    path: path.join(SCREENSHOTS, "15_document_upload_success.png"),
  });
  console.log("Saved 15_document_upload_success.png");
}

async function captureUploadValidation(page) {
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await waitForHtmx(page);
  await page.locator("#document-upload").scrollIntoViewIfNeeded();
  page.once("dialog", (dialog) => dialog.accept());
  await page.evaluate(() => {
    const input = document.getElementById("document");
    if (input) input.removeAttribute("required");
  });
  await page.locator("#upload-submit").click();
  await page.waitForTimeout(400);
  await page.locator("#document-upload").screenshot({
    path: path.join(SCREENSHOTS, "16_document_upload_validation.png"),
  });
  console.log("Saved 16_document_upload_validation.png (client validation)");
}

async function captureUploadError(page) {
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await waitForHtmx(page);
  await page.locator("#document-upload").scrollIntoViewIfNeeded();
  const badFile = path.join(SCREENSHOTS, "_bad_upload.exe");
  fs.writeFileSync(badFile, "fake");
  try {
    page.once("dialog", (dialog) => dialog.accept());
    await page.locator("#document").setInputFiles(badFile);
    await page.locator("#upload-submit").click();
    await page.waitForTimeout(500);
    await page.locator("#document-upload").screenshot({
      path: path.join(SCREENSHOTS, "17_document_upload_type_rejected.png"),
    });
    console.log("Saved 17_document_upload_type_rejected.png");
  } finally {
    fs.unlinkSync(badFile);
  }
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
    path: path.join(SCREENSHOTS, "11_pytest_passed.png"),
    fullPage: true,
  });
  await page.close();
  fs.unlinkSync(htmlPath);
  console.log("Saved 11_pytest_passed.png");
}

async function captureSmokeResults(browser) {
  await screenshotMarkdownFile(
    browser,
    path.join(ROOT, "evaluation", "smoke_results.md"),
    "12_kb_smoke_evaluation.png",
    "evaluation/smoke_results.md missing — run scripts/kb_smoke_test.py first",
  );
}

async function captureCorpusCatalog(browser) {
  const md = extractCorpusMarkdown();
  const htmlPath = path.join(SCREENSHOTS, "_corpus_preview.html");
  fs.writeFileSync(htmlPath, markdownToSimpleHtml(md));
  const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });
  await page.goto(`file:///${htmlPath.replace(/\\/g, "/")}`);
  await page.waitForTimeout(400);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "18_dataset_corpus.png"),
    fullPage: true,
  });
  await page.close();
  fs.unlinkSync(htmlPath);
  console.log("Saved 18_dataset_corpus.png");
}

async function captureQaShowcase(browser) {
  await screenshotMarkdownFile(
    browser,
    path.join(ROOT, "evaluation", "qa_showcase.md"),
    "19_sample_questions_answers.png",
    "evaluation/qa_showcase.md missing — run scripts/kb_smoke_test.py first",
  );
}

const pytestOnly = process.argv.includes("--pytest-only");
const mvpOnly = process.argv.includes("--mvp-only");

async function main() {
  fs.mkdirSync(SCREENSHOTS, { recursive: true });
  const browser = await chromium.launch({ headless: true });

  if (mvpOnly) {
    const context = await browser.newContext({
      viewport: VIEWPORT,
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    await captureMvpWorkflow(page);
    await context.close();
    await browser.close();
    console.log("Done — 13_mvp_workflow.png");
    return;
  }

  if (pytestOnly) {
    await capturePytest(browser);
    await browser.close();
    console.log("Done — 11_pytest_passed.png");
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
  await captureUploadValidation(page);
  await captureUploadError(page);
  await captureUploadSuccess(page);
  await page.close();

  await capturePytest(browser);
  await captureSmokeResults(browser);
  await captureCorpusCatalog(browser);
  await captureQaShowcase(browser);
  await browser.close();
  console.log("Done — screenshots 07–09, 11–19 in screenshots/");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
