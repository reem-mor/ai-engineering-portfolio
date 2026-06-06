/**
 * Capture the PITER AiOps live-demo screenshots from the `/console` surface.
 *
 * These map 1:1 to the class live-demo validation points and live in
 * `screenshots/console_demo/`. They are SEPARATE from the React SPA
 * submission set (07-19) so neither clobbers the other.
 *
 * Prereqs:
 *   docker compose up --build -d          → http://localhost:8080/console
 *   cd scripts && npm install && npx playwright install chromium
 *   node capture_console_demo.mjs
 *
 * Optional env:
 *   APP_URL                (default http://localhost:8080)
 *   PYTEST_OUTPUT_FILE     path to a captured `pytest` text log → 11_pytest.png
 *   SMOKE_MD_FILE          path to a smoke-results markdown → 12_smoke_results.png
 *                          (defaults to evaluation/live_smoke_summary.md if present)
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const playwrightPath = path.join(__dirname, "node_modules", "playwright", "index.mjs");
const { chromium } = await import(pathToFileURL(playwrightPath).href);

const APP_URL = (process.env.APP_URL ?? "http://localhost:8080").replace(/\/$/, "");
const CONSOLE_URL = `${APP_URL}/console`;
const OUT_DIR = path.join(ROOT, "screenshots", "console_demo");
const DESKTOP = { width: 1440, height: 900 };
const MOBILE = { width: 390, height: 844 };
const FOLLOW_UP_QUESTION = "who do I escalate to?";

fs.mkdirSync(OUT_DIR, { recursive: true });

function save(name) {
  return path.join(OUT_DIR, name);
}

/** Section locator keyed off its <h2> heading text. */
function sectionByHeading(page, text) {
  return page.locator(".section", {
    has: page.locator("h2", { hasText: text }),
  });
}

async function fillDemoAlert(page) {
  await page.locator("#demoBtn").click();
  // Demo alert is fetched via /api/demo-alert and populated into inputs.
  await page.waitForFunction(
    () => document.querySelector("#service")?.value?.length > 0,
    undefined,
    { timeout: 15_000 },
  );
}

async function runTriage(page) {
  // Kick off triage WITHOUT awaiting so we can catch the loader mid-flight.
  const responsePromise = page.waitForResponse(
    (r) => r.url().includes("/api/triage") && r.request().method() === "POST",
    { timeout: 120_000 },
  );
  await page.locator("#triageBtn").click();
  const response = await responsePromise;
  if (!response.ok()) {
    throw new Error(`/api/triage failed with HTTP ${response.status()}`);
  }
  await page.locator("#result .card").waitFor({ state: "visible", timeout: 30_000 });
  await page.locator("#result h2", { hasText: "Cited answer" }).waitFor({ timeout: 30_000 });
}

async function captureDesktopFlow(browser) {
  const ctx = await browser.newContext({ viewport: DESKTOP, deviceScaleFactor: 2 });
  const page = await ctx.newPage();

  const consoleErrors = [];
  page.on("console", (m) => {
    if (m.type() === "error") consoleErrors.push(m.text());
  });

  // 1. App home — empty console.
  await page.goto(CONSOLE_URL, { waitUntil: "networkidle" });
  await page.locator("#alertForm").waitFor({ timeout: 15_000 });
  await page.waitForTimeout(400);
  await page.screenshot({ path: save("01_home.png"), fullPage: true });
  console.log("Saved 01_home.png");

  // 2. Demo alert loaded, before submit.
  await fillDemoAlert(page);
  await page.waitForTimeout(300);
  await page.screenshot({ path: save("02_demo_alert.png"), fullPage: true });
  console.log("Saved 02_demo_alert.png");

  // 3. Loading / agent-processing state — delay the triage response so the
  //    3-step loader is visible, then capture it.
  let releaseDelay;
  const delayGate = new Promise((resolve) => {
    releaseDelay = resolve;
  });
  await page.route("**/api/triage", async (route) => {
    await delayGate; // hold the response open until we have the screenshot
    await route.continue();
  });
  await page.locator("#triageBtn").click();
  await page.locator("#loader.on").waitFor({ timeout: 15_000 });
  await page.locator("#s1.done").waitFor({ timeout: 15_000 });
  await page.waitForTimeout(250);
  await page.screenshot({ path: save("03_loading.png"), fullPage: false });
  console.log("Saved 03_loading.png");
  releaseDelay();

  // Let the (already in-flight) triage settle and render the card.
  await page.locator("#result .card").waitFor({ state: "visible", timeout: 60_000 });
  await page.locator("#result h2", { hasText: "Cited answer" }).waitFor({ timeout: 60_000 });
  await page.waitForTimeout(500);

  const mode = (await page.locator("#result .pill").first().textContent())?.trim();
  console.log(`Triage rendered — mode pill: ${mode}`);

  // 4. Final triage card (full).
  await page.screenshot({ path: save("04_triage_card.png"), fullPage: true });
  console.log("Saved 04_triage_card.png");

  // 5-8. Section clips.
  const sections = [
    ["Citations", "05_citations.png"],
    ["Owner & escalation", "06_owner_escalation.png"],
    ["Business impact", "07_business_impact.png"],
    ["Similar incidents", "08_similar_incidents.png"],
  ];
  for (const [heading, file] of sections) {
    const loc = sectionByHeading(page, heading).first();
    await loc.scrollIntoViewIfNeeded();
    await loc.waitFor({ state: "visible", timeout: 15_000 });
    await page.waitForTimeout(150);
    await loc.screenshot({ path: save(file) });
    console.log(`Saved ${file}`);
  }

  // 9. Follow-up using session memory.
  await page.locator("#followInput").scrollIntoViewIfNeeded();
  await page.locator("#followInput").fill(FOLLOW_UP_QUESTION);
  const followResp = page.waitForResponse(
    (r) => r.url().includes("/api/follow-up") && r.request().method() === "POST",
    { timeout: 60_000 },
  );
  await page.locator("#followBtn").click();
  const fr = await followResp;
  if (!fr.ok()) throw new Error(`/api/follow-up failed with HTTP ${fr.status()}`);
  await page.locator("#followOut pre").waitFor({ timeout: 30_000 });
  await page.waitForTimeout(300);
  const followText = (await page.locator("#followOut").textContent()) ?? "";
  const followSection = sectionByHeading(page, "Follow-up").first();
  await followSection.scrollIntoViewIfNeeded();
  await followSection.screenshot({ path: save("09_followup_memory.png") });
  console.log(`Saved 09_followup_memory.png (memory marker: ${/from memory/.test(followText)})`);

  if (consoleErrors.length) {
    console.warn(`WARNING: ${consoleErrors.length} browser console error(s):`);
    consoleErrors.forEach((e) => console.warn(`  - ${e}`));
  } else {
    console.log("No browser console errors.");
  }

  await ctx.close();
  return { mode, memoryUsed: /from memory/.test(followText), consoleErrors };
}

async function captureMobileFlow(browser) {
  const ctx = await browser.newContext({ viewport: MOBILE, deviceScaleFactor: 2, isMobile: true });
  const page = await ctx.newPage();
  await page.goto(CONSOLE_URL, { waitUntil: "networkidle" });
  await page.locator("#alertForm").waitFor({ timeout: 15_000 });
  await fillDemoAlert(page);
  await runTriage(page);
  await page.waitForTimeout(500);
  await page.screenshot({ path: save("10_mobile.png"), fullPage: true });
  console.log("Saved 10_mobile.png");
  await ctx.close();
}

function textToHtml(title, body) {
  const escaped = String(body)
    .replace(/^\uFEFF/, "") // strip UTF-8/UTF-16 BOM
    .replace(/\uFFFD/g, "") // strip stray replacement chars
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  return `<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
body{font-family:Consolas,Monaco,'Courier New',monospace;background:#0b1020;color:#e7ecf5;
padding:28px;margin:0;max-width:1100px}
h1{color:#6ea8fe;font-size:18px;margin:0 0 14px;font-family:Segoe UI,sans-serif}
pre{white-space:pre-wrap;font-size:13px;line-height:1.5;margin:0}
</style></head><body><h1>${title}</h1><pre>${escaped}</pre></body></html>`;
}

async function renderTextToPng(browser, title, body, outName) {
  const htmlPath = save(`_preview_${outName}.html`);
  fs.writeFileSync(htmlPath, textToHtml(title, body));
  const page = await browser.newPage({ viewport: { width: 1100, height: 900 } });
  await page.goto(pathToFileURL(htmlPath).href);
  await page.waitForTimeout(300);
  await page.screenshot({ path: save(outName), fullPage: true });
  await page.close();
  fs.unlinkSync(htmlPath);
  console.log(`Saved ${outName}`);
}

async function captureTerminalProof(browser) {
  // 11. pytest output (captured to a file by the shell before running this).
  const pytestFile =
    process.env.PYTEST_OUTPUT_FILE ?? path.join(ROOT, "evaluation", "pytest_output.txt");
  if (fs.existsSync(pytestFile)) {
    await renderTextToPng(
      browser,
      "pytest — PITER AiOps unit + integration suite",
      fs.readFileSync(pytestFile, "utf8"),
      "11_pytest.png",
    );
  } else {
    console.warn(`Skipped 11_pytest.png — no pytest log at ${pytestFile}`);
  }

  // 12. Smoke / live-demo results markdown.
  const smokeFile =
    process.env.SMOKE_MD_FILE ?? path.join(ROOT, "evaluation", "live_smoke_summary.md");
  if (fs.existsSync(smokeFile)) {
    await renderTextToPng(
      browser,
      `Live smoke results — ${path.basename(smokeFile)}`,
      fs.readFileSync(smokeFile, "utf8"),
      "12_smoke_results.png",
    );
  } else {
    console.warn(`Skipped 12_smoke_results.png — no smoke file at ${smokeFile}`);
  }
}

async function main() {
  console.log(`Console demo capture → ${CONSOLE_URL}`);
  const browser = await chromium.launch();
  try {
    const result = await captureDesktopFlow(browser);
    await captureMobileFlow(browser);
    await captureTerminalProof(browser);
    console.log("\n=== Console demo capture summary ===");
    console.log(`mode:         ${result.mode}`);
    console.log(`memory_used:  ${result.memoryUsed}`);
    console.log(`console_errs: ${result.consoleErrors.length}`);
    console.log(`output dir:   ${OUT_DIR}`);
  } finally {
    await browser.close();
  }
}

await main();
