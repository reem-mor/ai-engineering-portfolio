/**
 * One-off release-readiness browser audit (Playwright Chromium).
 * Run: node scripts/browser_audit.mjs
 * Requires app at APP_URL (default http://127.0.0.1:8080).
 */
import { chromium } from "playwright";

const APP_URL = (process.env.APP_URL || "http://127.0.0.1:8080").replace(/\/$/, "");
const VIEWPORTS = [
  { name: "mobile", width: 390, height: 844 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "desktop", width: 1440, height: 900 },
];

const QUESTIONS = [
  "How do I handle a database failover in NJ/DGE?",
  "What is the MTTR target for P1 incidents?",
  "How do I restart services in the STAGE environment?",
  "What does the post-mortem process look like?",
];

function luminance([r, g, b]) {
  const srgb = [r, g, b].map((c) => {
    const v = c / 255;
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * srgb[0] + 0.7152 * srgb[1] + 0.0722 * srgb[2];
}

function contrastRatio(fg, bg) {
  const l1 = luminance(fg);
  const l2 = luminance(bg);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

async function auditViewport(browser, viewport) {
  const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height } });
  const consoleErrors = [];
  const failedRequests = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  page.on("requestfailed", (req) => {
    failedRequests.push(`${req.method()} ${req.url()} — ${req.failure()?.errorText || "failed"}`);
  });

  await page.goto(`${APP_URL}/#live-kb`, { waitUntil: "networkidle" });
  await page.waitForSelector("#live-kb-question", { timeout: 15000 });

  const layout = await page.evaluate(() => {
    const ta = document.querySelector("#live-kb-question");
    const btn = document.querySelector('[aria-label="Ask knowledge base"], [aria-label="Querying knowledge base"]');
    const overflow = document.documentElement.scrollWidth > window.innerWidth + 2;
    const taBox = ta?.getBoundingClientRect();
    const btnBox = btn?.getBoundingClientRect();
    return {
      overflow,
      textareaVisible: !!(taBox && taBox.width > 0 && taBox.height > 0),
      buttonVisible: !!(btnBox && btnBox.width > 0 && btnBox.height > 0),
    };
  });

  const contrast = await page.evaluate(() => {
    const body = document.body;
    const sample = document.querySelector("#live-kb p, #live-kb label");
    const csBody = getComputedStyle(body);
    const csText = getComputedStyle(sample || body);
    const parse = (c) => {
      const m = c.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      return m ? [+m[1], +m[2], +m[3]] : [0, 0, 0];
    };
    return {
      bodyColor: csBody.backgroundColor,
      textColor: csText.color,
      bodyRgb: parse(csBody.backgroundColor),
      textRgb: parse(csText.color),
    };
  });
  const ratio = contrastRatio(contrast.textRgb, contrast.bodyRgb);

  let questionResult = null;
  if (viewport.name === "desktop") {
    const q = QUESTIONS[0];
    await page.fill("#live-kb-question", q);
    const askBtn = page.getByRole("button", { name: /Ask knowledge base/i });
    const loadingPromise = page.waitForSelector('[aria-busy="true"]', { timeout: 5000 }).catch(() => null);
    const t0 = Date.now();
    await askBtn.click();
    await loadingPromise;
    const hadLoading = (await page.locator('[aria-busy="true"]').count()) > 0;
    await page.waitForSelector("#live-kb .rounded-xl.border", { timeout: 60000 });
    await page.waitForFunction(
      () => !document.querySelector('[aria-label="Querying knowledge base"]'),
      { timeout: 60000 },
    );
    const latencyMs = Date.now() - t0;
    const dupCheck = await page.evaluate(() => {
      const answerBlocks = [...document.querySelectorAll("#live-kb .rounded-xl.border.bg-background\\/60 p")];
      const texts = answerBlocks.map((el) => el.textContent?.trim()).filter(Boolean);
      const unique = new Set(texts);
      return { paragraphCount: texts.length, duplicateParagraphs: texts.length !== unique.size, sample: texts.slice(0, 3) };
    });
    questionResult = { question: q, latencyMs, hadLoading, dupCheck };
  }

  await page.close();
  return {
    viewport: viewport.name,
    layoutOk: !layout.overflow && layout.textareaVisible && layout.buttonVisible,
    layout,
    contrastRatio: ratio.toFixed(2),
    contrastPassAA: ratio >= 4.5,
    consoleErrors,
    failedRequests,
    questionResult,
  };
}

async function auditQuestions(browser) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(`${APP_URL}/#live-kb`, { waitUntil: "networkidle" });
  await page.waitForSelector("#live-kb-question");

  const results = [];
  for (const q of QUESTIONS) {
    await page.fill("#live-kb-question", q);
    const t0 = Date.now();
    await page.getByRole("button", { name: /Ask knowledge base/i }).click();
    await page.waitForFunction(
      () => !document.querySelector('[aria-label="Querying knowledge base"]'),
      { timeout: 60000 },
    );
    const latencyMs = Date.now() - t0;
    const payload = await page.evaluate(() => {
      const section = document.querySelector("#live-kb");
      const answerText = section?.innerText || "";
      const summaryMatches = (answerText.match(/Summary:/g) || []).length;
      const answerHeaders = (answerText.match(/\bAnswer\b/g) || []).length;
      const citationCards = section?.querySelectorAll(".grid.gap-3 .rounded-lg.border").length ?? 0;
      return {
        hasAnswer: answerText.includes("Answer") || answerText.includes("Summary"),
        summaryMatches,
        answerHeaders,
        citationCards,
        preview: answerText.slice(0, 400),
      };
    });
    results.push({ question: q, latencyMs, ...payload, slow: latencyMs > 10000 });
  }
  await page.close();
  return results;
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  try {
    const viewportResults = [];
    for (const vp of VIEWPORTS) {
      viewportResults.push(await auditViewport(browser, vp));
    }
    const questions = await auditQuestions(browser);
    console.log(JSON.stringify({ appUrl: APP_URL, viewportResults, questions }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
