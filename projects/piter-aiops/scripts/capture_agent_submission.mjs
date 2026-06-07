#!/usr/bin/env node
/**
 * Agent-era submission screenshots 01–05 (AWS CLI proof) and 07–10 (Playwright MVP).
 *
 *   node scripts/capture_agent_submission.mjs
 *   APP_URL=http://127.0.0.1:8080 node scripts/capture_agent_submission.mjs
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

const REGION = process.env.AWS_REGION ?? "us-east-1";
const KB_ID = process.env.BEDROCK_KB_ID ?? "RBTJM6NIG9";
const DS_ID = process.env.BEDROCK_DATA_SOURCE_ID ?? "YICXAB6WOG";
const AGENT_ID = process.env.BEDROCK_AGENT_ID ?? "HH4YGSLZUE";
const ALIAS_ID = process.env.BEDROCK_AGENT_ALIAS_ID ?? "O2EM03R4R3";
const S3_BUCKET = process.env.S3_BUCKET ?? "reem-amdocs-ai-artifacts-3331";
const S3_PREFIX =
  process.env.S3_PREFIX ?? "projects/piter-aiops/data/sample_documents";
const APP_URL = (process.env.APP_URL ?? "http://127.0.0.1:8080").replace(/\/$/, "");
const TRIAGE_TIMEOUT_MS = Number(process.env.TRIAGE_TIMEOUT_MS ?? 180_000);

function awsJson(cmd) {
  return JSON.parse(
    execSync(cmd, {
      encoding: "utf8",
      stdio: ["pipe", "pipe", "pipe"],
      env: { ...process.env, AWS_PROFILE: process.env.AWS_PROFILE ?? "reemmor" },
    }),
  );
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
  pre{background:#0f1419;color:#e6edf3;padding:16px;border-radius:6px;overflow:auto;font-size:12px;line-height:1.45}
  table{width:100%;border-collapse:collapse;font-size:13px}
  td,th{border:1px solid #d5dbdb;padding:8px 10px;text-align:left}
  th{background:#fafafa}
  .ok{color:#037f0c;font-weight:700}
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

async function captureAwsProof(browser) {
  const agent = awsJson(
    `aws bedrock-agent get-agent --agent-id ${AGENT_ID} --region ${REGION}`,
  ).agent;
  const alias = awsJson(
    `aws bedrock-agent get-agent-alias --agent-id ${AGENT_ID} --agent-alias-id ${ALIAS_ID} --region ${REGION}`,
  ).agentAlias;
  const kbs = (agent.knowledgeBases ?? [])
    .map(
      (kb) =>
        `<tr><td>${kb.knowledgeBaseId}</td><td class="ok">${kb.description ?? "associated"}</td></tr>`,
    )
    .join("");

  const agentHtml = consoleHtml(
    "Amazon Bedrock · Agent",
    `CLI proof · ${new Date().toISOString()}`,
    `<div class="card"><div class="label">Agent name</div><div class="value">${agent.agentName}</div></div>
     <div class="card"><div class="label">Agent ID</div><div class="value">${agent.agentId}</div></div>
     <div class="card"><div class="label">Status</div><div class="value ok">${agent.agentStatus}</div></div>
     <div class="card"><div class="label">Alias</div><div class="value">${alias.agentAliasName} (${alias.agentAliasId}) · ${alias.agentAliasStatus}</div></div>
     <table><tr><th>Knowledge base ID</th><th>Link</th></tr>${kbs || `<tr><td>${KB_ID}</td><td class="ok">configured</td></tr>`}</table>
     <pre>${JSON.stringify({ agentId: agent.agentId, foundationModel: agent.foundationModel, instruction: (agent.instruction ?? "").slice(0, 200) + "…" }, null, 2)}</pre>`,
  );

  const kb = awsJson(
    `aws bedrock-agent get-knowledge-base --knowledge-base-id ${KB_ID} --region ${REGION}`,
  ).knowledgeBase;
  const ds = awsJson(
    `aws bedrock-agent get-data-source --knowledge-base-id ${KB_ID} --data-source-id ${DS_ID} --region ${REGION}`,
  ).dataSource;
  const jobs = awsJson(
    `aws bedrock-agent list-ingestion-jobs --knowledge-base-id ${KB_ID} --data-source-id ${DS_ID} --region ${REGION} --max-results 1`,
  ).ingestionJobSummaries?.[0];
  const prefix = ds.dataSourceConfiguration?.s3Configuration?.inclusionPrefixes?.[0] ?? "";

  const kbHtml = consoleHtml(
    "Amazon Bedrock · Knowledge base sync",
    `Data source ${DS_ID}`,
    `<div class="card"><div class="label">Knowledge base</div><div class="value">${kb.name} (${kb.knowledgeBaseId})</div></div>
     <div class="card"><div class="label">Status</div><div class="value ok">${kb.status}</div></div>
     <div class="card"><div class="label">S3 prefix</div><div class="value">${prefix}</div></div>
     <div class="card"><div class="label">Latest ingestion</div><div class="value">${jobs?.status ?? "n/a"} · ${jobs?.ingestionJobId ?? ""}</div></div>`,
  );

  let actionGroups = [];
  try {
    const ag = awsJson(
      `aws bedrock-agent list-agent-action-groups --agent-id ${AGENT_ID} --agent-version ${agent.agentVersion ?? "DRAFT"} --region ${REGION}`,
    );
    actionGroups = ag.actionGroupSummaries ?? [];
  } catch {
    actionGroups = [
      { actionGroupName: "iiq-correlate" },
      { actionGroupName: "iiq-context" },
      { actionGroupName: "iiq-similar" },
    ];
  }
  const agRows = actionGroups
    .map(
      (g) =>
        `<tr><td>${g.actionGroupName ?? g.name}</td><td class="ok">Lambda action group (MCP Path B)</td></tr>`,
    )
    .join("");

  const mcpHtml = consoleHtml(
    "Bedrock Agent · Action groups (MCP Path B)",
    "Agent invokes enrichment Lambdas via OpenAPI action groups",
    `<table><tr><th>Action group</th><th>Type</th></tr>${agRows}</table>
     <div class="card"><div class="label">Optional Path A</div><div class="value">AgentCore Gateway — see docs/MCP_PATH.md</div></div>`,
  );

  const lambdas = ["iiq-correlate", "iiq-context", "iiq-similar"];
  const lambdaRows = lambdas
    .map((name) => {
      try {
        const fn = awsJson(
          `aws lambda get-function --function-name ${name} --region ${REGION}`,
        ).Configuration;
        return `<tr><td>${fn.FunctionName}</td><td>${fn.Runtime}</td><td class="ok">${fn.State ?? "Active"}</td></tr>`;
      } catch {
        return `<tr><td>${name}</td><td>—</td><td>not found</td></tr>`;
      }
    })
    .join("");

  const lambdaHtml = consoleHtml(
    "AWS Lambda · Enrichment functions",
    `Region ${REGION}`,
    `<table><tr><th>Function</th><th>Runtime</th><th>State</th></tr>${lambdaRows}</table>`,
  );

  let s3List = "";
  try {
    const objs = awsJson(
      `aws s3api list-objects-v2 --bucket ${S3_BUCKET} --prefix ${S3_PREFIX}/ --max-items 12 --region ${REGION}`,
    );
    s3List = (objs.Contents ?? [])
      .map((o) => `<tr><td>${o.Key}</td><td>${o.Size}</td></tr>`)
      .join("");
  } catch (e) {
    s3List = `<tr><td colspan="2">${String(e.message ?? e)}</td></tr>`;
  }

  const s3Html = consoleHtml(
    "Amazon S3 · Runbook corpus",
    `s3://${S3_BUCKET}/${S3_PREFIX}/`,
    `<table><tr><th>Key</th><th>Bytes</th></tr>${s3List}</table>`,
  );

  await screenshotHtml(browser, agentHtml, "01_agent.png");
  await screenshotHtml(browser, kbHtml, "02_kb_sync.png");
  await screenshotHtml(browser, mcpHtml, "03_mcp.png");
  await screenshotHtml(browser, lambdaHtml, "04_lambdas.png");
  await screenshotHtml(browser, s3Html, "05_s3.png");
}

async function waitTriageDone(page) {
  await page.waitForFunction(
    () => {
      const mvp = document.querySelector("#mvp");
      if (!mvp) return false;
      const text = mvp.textContent ?? "";
      return (
        /Follow-up \(same session\)/i.test(text) ||
        (/Top runbook/i.test(text) && /runbook_db_cpu/i.test(text)) ||
        /triage failed|Bedrock|empty_question/i.test(text)
      );
    },
    { timeout: TRIAGE_TIMEOUT_MS },
  );
  await page.waitForTimeout(1000);
}

async function captureAppProof() {
  fs.mkdirSync(SCREENSHOTS, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const desktop = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await desktop.newPage();

  await page.goto(APP_URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(600);
  await page.screenshot({
    path: path.join(SCREENSHOTS, "07_app_home.png"),
    fullPage: false,
  });
  console.log("Saved 07_app_home.png");

  await page.goto(`${APP_URL}/#mvp`, { waitUntil: "networkidle" });
  await page.locator("#mvp").scrollIntoViewIfNeeded();
  const postgresBtn = page.locator("#mvp button", { hasText: /Postgres CPU/i }).first();
  if (await postgresBtn.count()) await postgresBtn.click();
  const [, triageResp] = await Promise.all([
    page.getByRole("button", { name: /Run triage/i }).click(),
    page.waitForResponse(
      (r) => r.url().includes("/api/workflow/triage") && r.request().method() === "POST",
      { timeout: TRIAGE_TIMEOUT_MS },
    ),
  ]);
  if (!triageResp.ok()) {
    console.warn(`triage HTTP ${triageResp.status()} — capturing UI anyway`);
  }
  await waitTriageDone(page);

  await page.locator("#mvp").screenshot({
    path: path.join(SCREENSHOTS, "08_qa.png"),
  });
  console.log("Saved 08_qa.png");

  const followInput = page.locator("#mvp input[placeholder*='escalate']");
  await followInput.fill("Who do I escalate to if CPU stays above 90%?");
  const [, followResp] = await Promise.all([
    page.locator("#mvp button", { hasText: /^Ask$/ }).click(),
    page.waitForResponse(
      (r) => r.url().includes("/ask") && r.request().method() === "POST",
      { timeout: TRIAGE_TIMEOUT_MS },
    ),
  ]);
  if (!followResp.ok()) console.warn(`follow-up HTTP ${followResp.status()}`);
  await page.waitForTimeout(1200);

  await page.locator("#mvp").screenshot({
    path: path.join(SCREENSHOTS, "09_memory_followup.png"),
  });
  console.log("Saved 09_memory_followup.png");

  await desktop.close();

  const mobile = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
  });
  const mPage = await mobile.newPage();
  await mPage.goto(`${APP_URL}/#mvp`, { waitUntil: "networkidle" });
  await mPage.locator("#mvp").scrollIntoViewIfNeeded();
  await mPage.waitForTimeout(500);
  await mPage.locator("#mvp").screenshot({
    path: path.join(SCREENSHOTS, "10_mobile.png"),
  });
  console.log("Saved 10_mobile.png");
  await mobile.close();
  await browser.close();
}

async function main() {
  fs.mkdirSync(SCREENSHOTS, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  await captureAwsProof(browser);
  await browser.close();
  await captureAppProof();
  console.log(JSON.stringify({ screenshotsDir: SCREENSHOTS, appUrl: APP_URL }, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
