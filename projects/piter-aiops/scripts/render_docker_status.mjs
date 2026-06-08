import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const body = fs.readFileSync(path.join(ROOT, "evaluation", "docker_status.txt"), "utf8");
const htmlPath = path.join(__dirname, "_docker.html");
const escaped = body.replace(/&/g, "&amp;").replace(/</g, "&lt;");
fs.writeFileSync(
  htmlPath,
  `<!DOCTYPE html><html><head><meta charset="utf-8"/></head><body style="font-family:Consolas,monospace;background:#0b1020;color:#e7ecf5;padding:24px;margin:0"><h1 style="font-family:Segoe UI,sans-serif;color:#6ea8fe;font-size:16px">Docker — PITER AiOps</h1><pre>${escaped}</pre></body></html>`,
);
const { chromium } = await import(
  pathToFileURL(path.join(__dirname, "node_modules", "playwright", "index.mjs")).href
);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 900, height: 320 } });
await page.goto(pathToFileURL(htmlPath).href);
await page.screenshot({
  path: path.join(ROOT, "screenshots", "final", "15_docker_running.png"),
  fullPage: true,
});
await browser.close();
fs.unlinkSync(htmlPath);
console.log("15_docker_running.png");
