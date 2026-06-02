#!/usr/bin/env node
/**
 * Capture Tier-1 app screenshots 07–09 against APP_URL.
 *   07_app_homepage_public.png         viewport only (hero, 1440×900)
 *   08_app_question_and_answer.png     #live-kb element (grounded answer)
 *   08b_app_citations_expanded.png     #live-kb element (citations expanded)
 *   09_app_refusal_or_low_confidence.png  #live-kb element (off-topic refusal)
 *
 * Set SKIP_HOMEPAGE=1 to skip overwriting 07 (e.g. keep an EC2 URL-bar capture).
 *
 * Prereq: app reachable with working Bedrock credentials.
 *   APP_URL="http://<public-ip>:8080" node scripts/capture_public_app.mjs
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const SHOTS = path.join(ROOT, "screenshots");
const playwrightPath = path.join(__dirname, "node_modules", "playwright", "index.mjs");
const { chromium } = await import(pathToFileURL(playwrightPath).href);
const APP_URL = (process.env.APP_URL ?? "http://127.0.0.1:8080").replace(/\/$/, "");
const SKIP_HOMEPAGE = process.env.SKIP_HOMEPAGE === "1";
const SQL_QUESTION = "Postgres CPU is 95% on prod-db-1 — what is the runbook?";
const REFUSAL_QUESTION = "What is the best restaurant in Tokyo?";

async function ask(page, question, { expectGrounded = true } = {}) {
  const section = page.locator("#live-kb");
  await section.scrollIntoViewIfNeeded();
  await section.locator("textarea").fill(question);
  const [resp] = await Promise.all([
    page.waitForResponse(
      (r) => r.url().includes("/ask") && r.request().method() === "POST",
      { timeout: 120_000 },
    ),
    section.getByRole("button", { name: /Ask Knowledge Base/i }).click(),
  ]);
  if (!resp.ok()) throw new Error(`/ask failed HTTP ${resp.status()}`);
  await page.waitForFunction(
    (grounded) => {
      const s = document.querySelector("#live-kb");
      if (!s) return false;
      const text = s.textContent || "";
      if (grounded) {
        return /Recommended steps/i.test(text) || !!s.querySelector("pre code");
      }
      return /Low confidence/i.test(text);
    },
    expectGrounded,
    { timeout: 60_000 },
  );
  await page.waitForTimeout(900);
}

async function screenshotLiveKb(page, filename) {
  const section = page.locator("#live-kb");
  await section.scrollIntoViewIfNeeded();
  await section.screenshot({ path: path.join(SHOTS, filename) });
}

async function main() {
  fs.mkdirSync(SHOTS, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();

  // 07 — homepage viewport (hero + nav; not full-page scroll)
  if (!SKIP_HOMEPAGE) {
    await page.goto(APP_URL, { waitUntil: "networkidle" });
    await page.waitForTimeout(700);
    await page.screenshot({
      path: path.join(SHOTS, "07_app_homepage_public.png"),
      fullPage: false,
    });
  }

  // 08 — grounded question + answer (#live-kb element)
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await ask(page, SQL_QUESTION, { expectGrounded: true });
  await screenshotLiveKb(page, "08_app_question_and_answer.png");

  // 08b — citations expanded (same session)
  const citToggle = page
    .locator("#live-kb button", { hasText: /Retrieved citations/i })
    .first();
  if (await citToggle.count()) {
    await citToggle.click();
    await page.waitForTimeout(600);
  }
  await screenshotLiveKb(page, "08b_app_citations_expanded.png");

  // 09 — off-topic refusal (#live-kb element)
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await ask(page, REFUSAL_QUESTION, { expectGrounded: false });
  await screenshotLiveKb(page, "09_app_refusal_or_low_confidence.png");

  await browser.close();
  const saved = ["08", "08b", "09"];
  if (!SKIP_HOMEPAGE) saved.unshift("07");
  console.log(JSON.stringify({ appUrl: APP_URL, saved }, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
