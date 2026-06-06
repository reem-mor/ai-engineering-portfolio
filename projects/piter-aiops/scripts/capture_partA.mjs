#!/usr/bin/env node
/**
 * Part A verification + screenshots for the redesigned ANSWER OUTPUT section.
 * Exercises: code blocks + syntax highlight, Copy button, destructive flag,
 * numbered steps, collapsible citations — at 390 / 768 / 1440.
 *
 * Prereq: app running at APP_URL (default http://127.0.0.1:8080) with live AWS creds.
 *   node scripts/capture_partA.mjs
 *
 * Writes screenshots to screenshots/extras/partA_*.png (responsive proof only).
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const SHOTS = path.join(ROOT, "screenshots", "extras");
const playwrightPath = path.join(__dirname, "node_modules", "playwright", "index.mjs");
const { chromium } = await import(pathToFileURL(playwrightPath).href);
const APP_URL = (process.env.APP_URL ?? "http://127.0.0.1:8080").replace(/\/$/, "");

// A question whose grounded answer contains SQL (pg_stat_activity + cancel/terminate)
// so we can prove code-block rendering AND the destructive-SQL flag.
const SQL_QUESTION = "Postgres CPU is 95% on prod-db-1 — what is the runbook?";

function luminance([r, g, b]) {
  const s = [r, g, b].map((c) => {
    const v = c / 255;
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * s[0] + 0.7152 * s[1] + 0.0722 * s[2];
}
function contrast(fg, bg) {
  const l1 = luminance(fg);
  const l2 = luminance(bg);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}

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
  // Wait for the rendered answer (Recommended steps or a code block).
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

async function inspect(page) {
  return page.evaluate(() => {
    const s = document.querySelector("#live-kb");
    const parse = (c) => {
      const m = (c || "").match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      return m ? [+m[1], +m[2], +m[3]] : null;
    };
    const codeBlocks = [...s.querySelectorAll("pre code")];
    const copyButtons = [...s.querySelectorAll('button[aria-label="Copy code"]')];
    const numberedSteps = [...s.querySelectorAll("[data-step-badge]")];
    const langBadges = [...s.querySelectorAll("span")].filter((el) =>
      /^(SQL|bash|python|HTTP|JSON|text)$/.test((el.textContent || "").trim()),
    );
    // Destructive flag label rendered by CodeBlock when destructive.
    const destructive = [...s.querySelectorAll("span")].filter((el) =>
      /destructive/i.test(el.textContent || ""),
    ).length;
    // Contrast: answer paragraph text vs nearest card background.
    let answerContrast = null;
    const para = s.querySelector("p");
    if (para) {
      const cs = getComputedStyle(para);
      let bgEl = para;
      let bg = null;
      while (bgEl && !bg) {
        const b = getComputedStyle(bgEl).backgroundColor;
        if (b && b !== "rgba(0, 0, 0, 0)" && b !== "transparent") bg = b;
        bgEl = bgEl.parentElement;
      }
      const fg = parse(cs.color);
      const bgc = parse(bg) || [0, 0, 0];
      if (fg) answerContrast = +contrastLocal(fg, bgc).toFixed(2);
    }
    // Code text contrast vs code block bg.
    let codeContrast = null;
    if (codeBlocks[0]) {
      const pre = codeBlocks[0].closest("pre") || codeBlocks[0];
      const fg = parse(getComputedStyle(codeBlocks[0]).color);
      let el = pre;
      let bg = null;
      while (el && !bg) {
        const b = getComputedStyle(el).backgroundColor;
        if (b && b !== "rgba(0, 0, 0, 0)" && b !== "transparent") bg = b;
        el = el.parentElement;
      }
      const bgc = parse(bg) || [0, 0, 0];
      if (fg) codeContrast = +contrastLocal(fg, bgc).toFixed(2);
    }
    // Citations collapsed by default? find the toggle and its aria-expanded.
    const citToggle = [...s.querySelectorAll("button")].find((b) =>
      /Retrieved citations/i.test(b.textContent || ""),
    );
    const citationsExpanded = citToggle ? citToggle.getAttribute("aria-expanded") : null;

    function contrastLocal(fg, bg) {
      const lum = (c) => {
        const v = c.map((x) => {
          const u = x / 255;
          return u <= 0.03928 ? u / 12.92 : ((u + 0.055) / 1.055) ** 2.4;
        });
        return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
      };
      const l1 = lum(fg);
      const l2 = lum(bg);
      return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    }

    return {
      codeBlockCount: codeBlocks.length,
      copyButtonCount: copyButtons.length,
      langBadgeCount: langBadges.length,
      numberedStepCount: numberedSteps.length,
      destructiveFlagCount: destructive,
      citationsAriaExpanded: citationsExpanded,
      answerContrast,
      codeContrast,
    };
  });
}

async function main() {
  fs.mkdirSync(SHOTS, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    permissions: ["clipboard-read", "clipboard-write"],
  });
  const report = { appUrl: APP_URL, viewports: {} };
  const page = await ctx.newPage();
  const consoleErrors = [];
  page.on("console", (m) => m.type() === "error" && consoleErrors.push(m.text()));

  // --- 1440 desktop: answer + interactions (homepage covered by 07_app_homepage_public) ---
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await ask(page, SQL_QUESTION);
  await page.locator("#live-kb").screenshot({
    path: path.join(SHOTS, "partA_answer_1440.png"),
  });
  const desk = await inspect(page);

  // Copy button: click first, expect aria-label to flip to "Copied".
  let copyWorks = false;
  const firstCopy = page.locator('#live-kb button[aria-label="Copy code"]').first();
  if (await firstCopy.count()) {
    await firstCopy.click();
    await page.waitForTimeout(250);
    copyWorks =
      (await page.locator('#live-kb button[aria-label="Copied"]').count()) > 0;
  }

  const numberedStepsPresent = (desk.numberedStepCount ?? 0) > 0;

  // Citations: expand and screenshot.
  const citToggle = page
    .locator("#live-kb button", { hasText: /Retrieved citations/i })
    .first();
  let citationToggleWorks = false;
  if (await citToggle.count()) {
    const before = await citToggle.getAttribute("aria-expanded");
    await citToggle.click();
    await page.waitForTimeout(500);
    const after = await citToggle.getAttribute("aria-expanded");
    citationToggleWorks = before === "false" && after === "true";
    await page.locator("#live-kb").screenshot({
      path: path.join(SHOTS, "partA_answer_expanded_1440.png"),
    });
  }
  report.viewports["1440"] = {
    ...desk,
    copyWorks,
    numberedStepsPresent,
    citationToggleWorks,
  };

  // --- 768 tablet ---
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await ask(page, SQL_QUESTION);
  await page.locator("#live-kb").screenshot({
    path: path.join(SHOTS, "partA_answer_768.png"),
  });
  report.viewports["768"] = await inspect(page);

  // --- 390 mobile ---
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await ask(page, SQL_QUESTION);
  await page.locator("#live-kb").screenshot({
    path: path.join(SHOTS, "partA_answer_390.png"),
  });
  report.viewports["390"] = await inspect(page);

  report.consoleErrors = consoleErrors;
  await browser.close();
  console.log(JSON.stringify(report, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
