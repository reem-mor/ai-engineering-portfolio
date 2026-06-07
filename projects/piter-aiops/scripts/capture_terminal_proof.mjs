#!/usr/bin/env node
/**
 * Terminal proof screenshots: 11_docker_ps.png, 12_tests.png
 */
import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const SCREENSHOTS = path.join(ROOT, "screenshots");
const playwrightPath = path.join(__dirname, "node_modules", "playwright", "index.mjs");
const { chromium } = await import(pathToFileURL(playwrightPath).href);

const PYTHON =
  process.env.PYTHON ??
  (process.platform === "win32"
    ? path.join(ROOT, ".venv", "Scripts", "python.exe")
    : path.join(ROOT, ".venv", "bin", "python"));

function termHtml(title, cmd, output) {
  const esc = (s) =>
    s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return `<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
  body{margin:0;background:#0c0c0c;color:#cccccc;font-family:Consolas,"Cascadia Mono",monospace}
  .bar{background:#1e1e1e;padding:12px 16px;border-bottom:1px solid #333;font-size:13px;color:#9cdcfe}
  pre{margin:0;padding:20px;font-size:13px;line-height:1.5;white-space:pre-wrap}
  .prompt{color:#4ec9b0}
</style></head><body>
<div class="bar">${esc(title)}</div>
<pre><span class="prompt">$ </span>${esc(cmd)}\n\n${esc(output)}</pre>
</body></html>`;
}

async function shot(browser, html, name) {
  const p = path.join(SCREENSHOTS, `_term_${name}.html`);
  fs.writeFileSync(p, html);
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await page.goto(`file:///${p.replace(/\\/g, "/")}`);
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(SCREENSHOTS, name) });
  await page.close();
  fs.unlinkSync(p);
  console.log(`Saved ${name}`);
}

async function main() {
  fs.mkdirSync(SCREENSHOTS, { recursive: true });
  const dockerPs = execSync("docker ps --filter name=PITER AiOps", {
    encoding: "utf8",
  });
  let pytestOut = "";
  try {
    pytestOut = execSync(`"${PYTHON}" -m pytest -q`, {
      encoding: "utf8",
      cwd: ROOT,
      timeout: 300_000,
    });
  } catch (e) {
    pytestOut = (e.stdout ?? "") + (e.stderr ?? "") + (e.message ?? "");
  }

  const browser = await chromium.launch({ headless: true });
  await shot(
    browser,
    termHtml("docker ps — PITER AiOps container", "docker ps --filter name=PITER AiOps", dockerPs),
    "11_docker_ps.png",
  );
  await shot(
    browser,
    termHtml("pytest — unit tests", "python -m pytest -q", pytestOut.trim()),
    "12_tests.png",
  );
  await browser.close();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
