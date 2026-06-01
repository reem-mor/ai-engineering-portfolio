#!/usr/bin/env node
/**
 * Capture SPA (React default UI) screenshots 07–09 against the running app.
 *
 * Prereqs:
 *   docker compose up --build -d   -> http://localhost:8080 (SPA, live AWS creds)
 *
 *   node scripts/capture_spa_screenshots.mjs
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const SCREENSHOTS = path.join(ROOT, "screenshots");
const playwrightPath = path.join(__dirname, "node_modules", "playwright", "index.mjs");
const { chromium } = await import(pathToFileURL(playwrightPath).href);
const APP_URL = process.env.APP_URL ?? "http://localhost:8080";
const VIEWPORT = { width: 1440, height: 900 };

async function askInLiveKb(page, question) {
  const section = page.locator("#live-kb");
  await section.scrollIntoViewIfNeeded();
  await section.locator("textarea").fill(question);
  const [response] = await Promise.all([
    page.waitForResponse(
      (r) => r.url().includes("/ask") && r.request().method() === "POST",
      { timeout: 120_000 },
    ),
    section.getByRole("button", { name: /Ask Knowledge Base/i }).click(),
  ]);
  if (!response.ok()) {
    throw new Error(`/ask failed with HTTP ${response.status()}`);
  }
  // Let the answer + citations animate in.
  await page.waitForTimeout(1200);
}

async function main() {
  fs.mkdirSync(SCREENSHOTS, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: VIEWPORT });

  // 07 — homepage
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(800);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "07_app_homepage_public.png"),
    fullPage: true,
  });
  console.log("Saved 07_app_homepage_public.png (SPA homepage)");

  // 08 — grounded answer + citations
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await askInLiveKb(page, "Postgres CPU is 95% on prod-db-1 — what is the runbook?");
  await page.locator("#live-kb").screenshot({
    path: path.join(SCREENSHOTS, "08_app_question_and_answer.png"),
  });
  console.log("Saved 08_app_question_and_answer.png (SPA grounded answer)");

  // 09 — graceful refusal
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await askInLiveKb(page, "What is the best restaurant in Tokyo?");
  await page.locator("#live-kb").screenshot({
    path: path.join(SCREENSHOTS, "09_app_refusal_or_low_confidence.png"),
  });
  console.log("Saved 09_app_refusal_or_low_confidence.png (SPA refusal)");

  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
