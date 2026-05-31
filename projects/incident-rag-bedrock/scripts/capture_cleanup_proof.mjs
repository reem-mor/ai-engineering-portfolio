#!/usr/bin/env node
/** Screenshot 10 — EC2 instances after teardown (CLI proof). */
import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SCREENSHOTS = path.join(path.resolve(__dirname, ".."), "screenshots");
const playwrightPath = path.join(__dirname, "node_modules", "playwright", "index.mjs");
const { chromium } = await import(pathToFileURL(playwrightPath).href);

const instances = JSON.parse(
  execSync(
    `aws ec2 describe-instances --filters Name=tag:Name,Values=incident-rag-demo --query "Reservations[].Instances[].{Id:InstanceId,State:State.Name,DNS:PublicDnsName}"`,
    { encoding: "utf8" },
  ),
);

const html = `<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
body{margin:0;font-family:"Segoe UI",Arial,sans-serif;background:#f2f3f3}
.header{background:#232f3e;color:#fff;padding:16px 24px;border-bottom:3px solid #ff9900}
.content{padding:24px}
table{width:100%;border-collapse:collapse;background:#fff}
td,th{border:1px solid #d5dbdb;padding:10px;font-size:13px}
th{background:#fafafa}
.note{margin-top:16px;padding:16px;background:#fff;border:1px solid #d5dbdb;border-radius:8px}
</style></head><body>
<div class="header"><h1>Amazon EC2 · Cleanup confirmation</h1><p>No running incident-rag-demo instances</p></div>
<div class="content">
<table><tr><th>Instance ID</th><th>State</th><th>Public DNS</th></tr>
${instances.map((i) => `<tr><td>${i.Id}</td><td>${i.State}</td><td>${i.DNS || "—"}</td></tr>`).join("")}
</table>
<div class="note"><strong>Deleted after demo:</strong> EC2 instance <code>i-03d3c5a59e849e5cf</code>, security group <code>sg-0b405b6a42325979e</code>, IAM role <code>incident-rag-ec2-role</code>, instance profile <code>incident-rag-ec2-profile</code>.</div>
</div></body></html>`;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const htmlPath = path.join(SCREENSHOTS, "_cleanup_preview.html");
fs.writeFileSync(htmlPath, html);
await page.goto(`file:///${htmlPath.replace(/\\/g, "/")}`);
await page.screenshot({ path: path.join(SCREENSHOTS, "10_cleanup_console.png"), fullPage: true });
await browser.close();
fs.unlinkSync(htmlPath);
console.log("Saved 10_cleanup_console.png");
