#!/usr/bin/env node
/** EC2 proof screenshot 06_ec2.png (instance + security group). */
import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SCREENSHOTS = path.join(path.resolve(__dirname, ".."), "screenshots");
const playwrightPath = path.join(__dirname, "node_modules", "playwright", "index.mjs");
const { chromium } = await import(pathToFileURL(playwrightPath).href);

const INSTANCE_ID = process.env.EC2_INSTANCE_ID;
const SG_ID = process.env.EC2_SG_ID;
if (!INSTANCE_ID) {
  console.error("Set EC2_INSTANCE_ID (and optional EC2_SG_ID)");
  process.exit(1);
}

function awsJson(cmd) {
  return JSON.parse(execSync(cmd, { encoding: "utf8", env: { ...process.env, AWS_PROFILE: process.env.AWS_PROFILE ?? "reemmor" } }));
}

function consoleHtml(title, subtitle, bodyHtml) {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
  body{margin:0;font-family:Segoe UI,Arial,sans-serif;background:#f2f3f3;color:#16191f}
  .header{background:#232f3e;color:#fff;padding:16px 24px;border-bottom:3px solid #ff9900}
  .header h1{font-size:18px;margin:0 0 4px}
  .header p{margin:0;font-size:13px;color:#d5dbdb}
  .content{padding:24px;max-width:1100px}
  .card{background:#fff;border:1px solid #d5dbdb;border-radius:8px;padding:20px;margin-bottom:16px}
  pre{background:#0f1419;color:#e6edf3;padding:16px;border-radius:6px;font-size:12px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  td,th{border:1px solid #d5dbdb;padding:8px}
  th{background:#fafafa}
  .ok{color:#037f0c;font-weight:700}
</style></head><body>
<div class="header"><h1>${title}</h1><p>${subtitle}</p></div>
<div class="content">${bodyHtml}</div></body></html>`;
}

const inst = awsJson(
  `aws ec2 describe-instances --instance-ids ${INSTANCE_ID} --region us-east-1`,
).Reservations[0].Instances[0];
const sgId = SG_ID ?? inst.SecurityGroups?.[0]?.GroupId;
const sg = awsJson(`aws ec2 describe-security-groups --group-ids ${sgId} --region us-east-1`).SecurityGroups[0];
const sgRows = (sg.IpPermissions ?? [])
  .map((r) => {
    const port = r.FromPort === r.ToPort ? r.FromPort : `${r.FromPort}-${r.ToPort}`;
    const cidrs = (r.IpRanges ?? []).map((x) => x.CidrIp).join(", ");
    return `<tr><td>${r.IpProtocol}</td><td>${port}</td><td>${cidrs}</td></tr>`;
  })
  .join("");

const html = consoleHtml(
  "Amazon EC2 - PITER AiOps public demo",
  new Date().toISOString(),
  `<div class="card"><div class="value ok">${inst.State?.Name}</div>
   <table><tr><th>Name</th><th>Instance ID</th><th>Public IP</th><th>Type</th></tr>
   <tr><td>${inst.Tags?.find((t) => t.Key === "Name")?.Value ?? "piter-aiops-demo"}</td>
       <td>${inst.InstanceId}</td><td>${inst.PublicIpAddress}</td><td>${inst.InstanceType}</td></tr></table></div>
   <div class="card"><b>Security group ${sgId}</b>
   <table><tr><th>Protocol</th><th>Port</th><th>Source</th></tr>${sgRows}</table></div>
   <pre>${JSON.stringify({ PublicDnsName: inst.PublicDnsName, IamInstanceProfile: inst.IamInstanceProfile?.Arn }, null, 2)}</pre>`,
);

fs.mkdirSync(SCREENSHOTS, { recursive: true });
const browser = await chromium.launch({ headless: true });
const p = path.join(SCREENSHOTS, "_ec2_preview.html");
fs.writeFileSync(p, html);
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto(`file:///${p.replace(/\\/g, "/")}`);
await page.waitForTimeout(400);
await page.screenshot({ path: path.join(SCREENSHOTS, "06_ec2.png"), fullPage: true });
await browser.close();
fs.unlinkSync(p);
console.log("Saved 06_ec2.png");
