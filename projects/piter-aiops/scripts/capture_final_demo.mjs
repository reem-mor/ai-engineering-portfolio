/**
 * Capture presentation screenshots for the React SPA into screenshots/final/.
 *
 * Prereqs:
 *   docker compose up -d  → http://localhost:8080
 *   cd scripts && npm ci && npx playwright install chromium
 *   node capture_final_demo.mjs
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "screenshots", "final");
const playwrightPath = path.join(__dirname, "node_modules", "playwright", "index.mjs");
const { chromium } = await import(pathToFileURL(playwrightPath).href);

const APP_URL = (process.env.APP_URL ?? "http://localhost:8080").replace(/\/$/, "");
const VIEWPORT = { width: 1440, height: 900 };

fs.mkdirSync(OUT, { recursive: true });
const shot = (name) => path.join(OUT, name);

async function nav(page, label) {
  await page.getByRole("button", { name: label, exact: true }).click();
  await page.waitForTimeout(400);
}

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: VIEWPORT, deviceScaleFactor: 2 });

  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await page.waitForSelector("text=PITER AiOps", { timeout: 20_000 });

  await page.screenshot({ path: shot("01_dashboard.png"), fullPage: true });
  console.log("01_dashboard.png");

  await nav(page, "Investigations");
  await page.screenshot({ path: shot("02_investigations_table.png"), fullPage: true });
  console.log("02_investigations_table.png");

  await nav(page, "Alert Storm");
  await page.getByRole("button", { name: "Start alert storm" }).click();
  await page.waitForTimeout(2500);
  await page.screenshot({ path: shot("03_alert_storm_running.png"), fullPage: true });
  console.log("03_alert_storm_running.png");

  await page.waitForSelector("text=P1 bet-service", { timeout: 60_000 });
  await page.screenshot({ path: shot("04_p1_detected.png"), fullPage: true });
  console.log("04_p1_detected.png");

  const analyzeBtn = page.getByRole("button", { name: /Run PITER analysis/i });
  await analyzeBtn.click();
  await page.waitForResponse(
    (r) => r.url().includes("/api/triage") && r.request().method() === "POST",
    { timeout: 120_000 },
  );
  await page.waitForTimeout(1500);
  await page.screenshot({ path: shot("05_investigation_detail_triage.png"), fullPage: true });
  console.log("05_investigation_detail_triage.png");

  const citations = page.locator("text=RAG citations").first();
  if (await citations.isVisible()) {
    await citations.scrollIntoViewIfNeeded();
    await page.screenshot({ path: shot("06_rag_citations.png"), fullPage: false });
    console.log("06_rag_citations.png");
  }

  await nav(page, "MCP / Lambda Tools");
  await page.screenshot({ path: shot("07_lambda_mcp_tools.png"), fullPage: true });
  console.log("07_lambda_mcp_tools.png");

  await nav(page, "Context Memory");
  await page.screenshot({ path: shot("08_memory_followup_context.png"), fullPage: true });
  console.log("08_memory_followup_context.png");

  await nav(page, "Alert Storm");
  const escalateBtn = page.getByRole("button", { name: "Escalate on-call (SMS / email)" });
  if (await escalateBtn.isVisible()) {
    await escalateBtn.click();
    await page.waitForTimeout(600);
    await page.screenshot({ path: shot("09_escalation_preview.png"), fullPage: true });
    console.log("09_escalation_preview.png");
    await page.getByRole("button", { name: "Close" }).click();
    await page.waitForTimeout(400);
  }

  await page.screenshot({ path: shot("10_post_mortem_summary.png"), fullPage: true });
  console.log("10_post_mortem_summary.png");

  await nav(page, "Knowledge Base");
  await page.screenshot({ path: shot("11_knowledge_base.png"), fullPage: true });
  console.log("11_knowledge_base.png");

  const upload = page.locator('input[type="file"]').first();
  if (await upload.count()) {
    const sample = path.join(ROOT, "knowledge_base", "runbooks", "runbook_bet_service_critical.md");
    if (fs.existsSync(sample)) {
      await upload.setInputFiles(sample);
      await page.waitForTimeout(1200);
    }
  }
  await page.screenshot({ path: shot("12_upload_document_flow.png"), fullPage: true });
  console.log("12_upload_document_flow.png");

  await nav(page, "Architecture");
  await page.screenshot({ path: shot("13_architecture_settings.png"), fullPage: true });
  console.log("13_architecture_settings.png");

  await nav(page, "Settings");
  await page.screenshot({ path: shot("13b_settings_aws_status.png"), fullPage: true });
  console.log("13b_settings_aws_status.png");

  await browser.close();
  console.log(`\nSaved SPA screenshots → ${OUT}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
