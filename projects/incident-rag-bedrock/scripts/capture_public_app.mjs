#!/usr/bin/env node
/**
 * Capture submission shots 07/08/08b against APP_URL.
 *   07_app_homepage_public.png            homepage served from the public IP
 *   08_app_question_and_answer.png        grounded answer (Part A UI: code block + steps)
 *   08b_app_citations_expanded.png        same answer with citations expanded
 *
 * Prereq: app reachable at APP_URL with working Bedrock (instance profile).
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
const SKIP_HOMEPAGE =
  process.env.SKIP_HOMEPAGE === "1" ||
  /^https?:\/\/(127\.0\.0\.1|localhost)(:\d+)?$/i.test(APP_URL);
const SQL_QUESTION = "Postgres CPU is 95% on prod-db-1 — what is the runbook?";

async function ask(page, question) {
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
    () => {
      const s = document.querySelector("#live-kb");
      if (!s) return false;
      return /Recommended steps/i.test(s.textContent || "") || !!s.querySelector("pre code");
    },
    { timeout: 60_000 },
  );
  await page.waitForTimeout(900);
}

async function main() {
  fs.mkdirSync(SHOTS, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();

  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(700);

  // 07 — public homepage (skip when localhost to avoid overwriting EC2-captured 07)
  if (!SKIP_HOMEPAGE) {
    await page.screenshot({
      path: path.join(SHOTS, "07_app_homepage_public.png"),
      fullPage: true,
    });
  }

  // 08 — grounded question + answer
  await ask(page, SQL_QUESTION);
  await page.locator("#live-kb").scrollIntoViewIfNeeded();
  await page.screenshot({
    path: path.join(SHOTS, "08_app_question_and_answer.png"),
    fullPage: true,
  });

  // 08b — citations expanded
  const citToggle = page
    .locator("#live-kb button", { hasText: /Retrieved citations/i })
    .first();
  if (await citToggle.count()) {
    await citToggle.click();
    await page.waitForTimeout(600);
  }
  await page.screenshot({
    path: path.join(SHOTS, "08b_app_citations_expanded.png"),
    fullPage: true,
  });

  await browser.close();
  const saved = ["08", "08b"];
  if (!SKIP_HOMEPAGE) saved.unshift("07");
  console.log(JSON.stringify({ appUrl: APP_URL, saved }, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
