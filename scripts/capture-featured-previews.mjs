/**
 * Capture featured-work preview images from GitHub README pages.
 * Requires: npm install playwright (or use frontend/node_modules in capstone)
 *
 *   node scripts/capture-featured-previews.mjs
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "docs", "screenshots", "featured");

const playwrightCandidates = [
  path.join(ROOT, "projects", "incident-assistant-rag", "frontend", "node_modules", "playwright", "index.mjs"),
  path.join(ROOT, "homework", "hw07", "node_modules", "playwright", "index.mjs"),
];

function resolvePlaywright() {
  for (const p of playwrightCandidates) {
    if (fs.existsSync(p)) return p;
  }
  throw new Error("Install Playwright in capstone frontend: cd projects/incident-assistant-rag/frontend && npm install && npx playwright install chromium");
}

const { chromium } = await import(pathToFileURL(resolvePlaywright()).href);

const targets = [
  {
    file: "course-bot-architecture.png",
    url: "https://github.com/reem-mor/course-assistant-bot",
    heading: "Architecture",
    height: 560,
  },
  {
    file: "piter-see-it-working.png",
    url: "https://github.com/reem-mor/piter-aiops#see-it-working",
    heading: "See it working",
    height: 640,
  },
];

fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

for (const t of targets) {
  await page.goto(t.url, { waitUntil: "networkidle", timeout: 60_000 });
  await page.waitForTimeout(2000);
  const heading = page.getByRole("heading", { name: t.heading });
  await heading.scrollIntoViewIfNeeded();
  await page.waitForTimeout(1200);
  const box = await heading.boundingBox();
  if (!box) {
    console.warn(`Skip ${t.file}: heading not found`);
    continue;
  }
  const outPath = path.join(OUT, t.file);
  await page.screenshot({
    path: outPath,
    clip: {
      x: Math.max(0, box.x - 24),
      y: box.y - 8,
      width: Math.min(960, 960),
      height: t.height,
    },
  });
  console.log(`Saved ${outPath}`);
}

await browser.close();
