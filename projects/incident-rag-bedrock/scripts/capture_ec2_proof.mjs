#!/usr/bin/env node
/**
 * Render EC2 / cleanup proof screenshots 04–06 and 10 from AWS CLI + SSH output.
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

const INSTANCE_ID = process.env.EC2_INSTANCE_ID ?? "i-03d3c5a59e849e5cf";
const SG_ID = process.env.EC2_SG_ID ?? "sg-0b405b6a42325979e";
const SSH_KEY = process.env.EC2_SSH_KEY ?? "C:/Users/reemm/Desktop/oz_ve_roah/AWS/amdocs-course-key.pem";
const PUBLIC_DNS =
  process.env.EC2_PUBLIC_DNS ?? "ec2-100-53-32-194.compute-1.amazonaws.com";

function awsJson(cmd) {
  return JSON.parse(execSync(cmd, { encoding: "utf8" }));
}

function consoleHtml(title, subtitle, bodyHtml) {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
  body{margin:0;font-family:"Segoe UI",Arial,sans-serif;background:#f2f3f3;color:#16191f}
  .header{background:#232f3e;color:#fff;padding:16px 24px;border-bottom:3px solid #ff9900}
  .header h1{font-size:18px;margin:0 0 4px;font-weight:600}
  .header p{margin:0;font-size:13px;color:#d5dbdb}
  .content{padding:24px;max-width:1100px}
  .card{background:#fff;border:1px solid #d5dbdb;border-radius:8px;padding:20px;margin-bottom:16px}
  .label{font-size:12px;color:#545b64;text-transform:uppercase}
  .value{font-size:15px;margin-top:4px;font-weight:600}
  pre{background:#0f1419;color:#e6edf3;padding:16px;border-radius:6px;overflow:auto;font-size:12px;line-height:1.45;white-space:pre-wrap}
  table{width:100%;border-collapse:collapse;font-size:13px}
  td,th{border:1px solid #d5dbdb;padding:8px 10px;text-align:left}
  th{background:#fafafa}
  .ok{color:#037f0c;font-weight:700}
  .term{background:#0c0c0c;color:#cccccc;padding:20px;border-radius:8px;font-family:Consolas,monospace;font-size:13px}
</style></head><body>
<div class="header"><h1>${title}</h1><p>${subtitle}</p></div>
<div class="content">${bodyHtml}</div>
</body></html>`;
}

async function screenshotHtml(browser, html, filename) {
  const htmlPath = path.join(SCREENSHOTS, `_preview_${filename}.html`);
  fs.writeFileSync(htmlPath, html);
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(`file:///${htmlPath.replace(/\\/g, "/")}`);
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(SCREENSHOTS, filename), fullPage: true });
  await page.close();
  fs.unlinkSync(htmlPath);
  console.log(`Saved ${filename}`);
}

async function main() {
  fs.mkdirSync(SCREENSHOTS, { recursive: true });
  const inst = awsJson(
    `aws ec2 describe-instances --instance-ids ${INSTANCE_ID} --query "Reservations[0].Instances[0]"`,
  );
  const sg = awsJson(`aws ec2 describe-security-groups --group-ids ${SG_ID}`).SecurityGroups[0];

  const ec2Html = consoleHtml(
    "Amazon EC2 · Instances",
    "Public demo instance for incident-rag-bedrock",
    `<table><tr><th>Name</th><th>Instance ID</th><th>State</th><th>Public DNS</th></tr>
     <tr><td>${inst.Tags?.find((t) => t.Key === "Name")?.Value ?? "incident-rag-demo"}</td>
         <td>${inst.InstanceId}</td><td class="ok">${inst.State?.Name}</td>
         <td>${inst.PublicDnsName}</td></tr></table>
     <pre>${JSON.stringify({ InstanceId: inst.InstanceId, PublicIpAddress: inst.PublicIpAddress, PublicDnsName: inst.PublicDnsName, InstanceType: inst.InstanceType, IamInstanceProfile: inst.IamInstanceProfile }, null, 2)}</pre>`,
  );

  const sgRules = (sg.IpPermissions ?? [])
    .map((r) => {
      const port = r.FromPort === r.ToPort ? r.FromPort : `${r.FromPort}-${r.ToPort}`;
      const cidrs = (r.IpRanges ?? []).map((x) => x.CidrIp).join(", ");
      return `<tr><td>${r.IpProtocol}</td><td>${port}</td><td>${cidrs}</td></tr>`;
    })
    .join("");
  const sgHtml = consoleHtml(
    "Amazon EC2 · Security groups · incident-rag-sg",
    `Inbound rules for ${SG_ID}`,
    `<table><tr><th>Protocol</th><th>Port</th><th>Source</th></tr>${sgRules}</table>`,
  );

  const dockerPs = execSync(
    `ssh -i "${SSH_KEY}" -o StrictHostKeyChecking=no ec2-user@${PUBLIC_DNS} "sudo docker ps"`,
    { encoding: "utf8" },
  );
  const dockerHtml = consoleHtml(
    "EC2 SSH session · docker ps",
    `ec2-user@${PUBLIC_DNS}`,
    `<div class="term"><pre>${dockerPs.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</pre></div>`,
  );

  const browser = await chromium.launch({ headless: true });
  await screenshotHtml(browser, ec2Html, "04_ec2_instance_running.png");
  await screenshotHtml(browser, sgHtml, "05_security_group_rules.png");
  await screenshotHtml(browser, dockerHtml, "06_docker_ps_on_ec2.png");
  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
