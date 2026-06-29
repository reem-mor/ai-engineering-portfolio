import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  KB_ANSWER_HINTS,
  KB_COLLECTION_NAME,
  PROMPTS,
  TOOL_ANSWER_HINTS,
  TOOL_OPERATION_HINTS,
  TOOL_SERVER_URL,
} from "./fixtures/prompts.js";
import {
  attachKnowledgeCollection,
  clearAllChats,
  configureMockLlmConnection,
  createKnowledgeCollection,
  dismissModals,
  enableToolsInChat,
  MOCK_LLM_MODEL,
  registerToolServer,
  screenshot,
  screenshotChatExchange,
  selectChatModel,
  sendChatMessage,
  startNewChat,
  uploadCsvToCollection,
  waitForAssistantReply,
  waitForKnowledgeIndexed,
  waitForToolInvocation,
} from "./helpers/open-webui.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SCREENSHOT_DIR = path.resolve(__dirname, "../screenshots");
const CSV_PATH = path.resolve(__dirname, "../data/netflix_titles.csv");
const TOOL_SERVER_BASE =
  process.env.TOOL_SERVER_BASE_URL ??
  process.env.TOOL_SERVER_URL ??
  "http://localhost:5005";
const TOOL_SERVER_HEALTH = `${TOOL_SERVER_BASE.replace(/\/$/, "")}/health`;
const OPEN_WEBUI_URL = process.env.OPEN_WEBUI_URL ?? "http://localhost:3001";
const MOCK_LLM_HEALTH =
  (process.env.HW07_MOCK_LLM_URL ?? "http://localhost:8088").replace(/\/v1\/?$/, "") + "/health";
const STACK_START_HINT =
  process.platform === "win32"
    ? "Run scripts/start-stack.ps1"
    : "Run scripts/start-stack.sh (or pip open-webui + ollama on host)";

function cleanScreenshotDir(): void {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  for (const file of fs.readdirSync(SCREENSHOT_DIR)) {
    if (file.endsWith(".png")) {
      fs.unlinkSync(path.join(SCREENSHOT_DIR, file));
    }
  }
}

test.describe.serial("HW07 submission screenshots", () => {
  test.beforeAll(async ({ request }) => {
    cleanScreenshotDir();

    const [webui, tools, mockLlm] = await Promise.all([
      request.get(OPEN_WEBUI_URL).catch(() => null),
      request.get(TOOL_SERVER_HEALTH).catch(() => null),
      request.get(MOCK_LLM_HEALTH).catch(() => null),
    ]);
    test.skip(!webui?.ok(), `Open WebUI not running at ${OPEN_WEBUI_URL}. ${STACK_START_HINT}`);
    test.skip(!tools?.ok(), `Tool server not running. ${STACK_START_HINT}`);
    test.skip(
      !mockLlm?.ok(),
      `Mock LLM not running at ${MOCK_LLM_HEALTH}. Start: python homework/hw07/scripts/mock-llm-server.py`,
    );

    const health = await tools!.json();
    expect(health.status).toBe("ok");

    await configureMockLlmConnection(request);
    await clearAllChats(request);
  });

  test("01-03 knowledge base upload and index", async ({ page }) => {
    test.setTimeout(600_000);
    await page.goto(`${OPEN_WEBUI_URL}/workspace/knowledge/create`, { waitUntil: "domcontentloaded" });
    await dismissModals(page);
    await createKnowledgeCollection(page, KB_COLLECTION_NAME);
    await screenshot(page, path.join(SCREENSHOT_DIR, "01-kb-collection-created.png"));

    await uploadCsvToCollection(page, CSV_PATH, KB_COLLECTION_NAME);
    await screenshot(page, path.join(SCREENSHOT_DIR, "02-kb-csv-uploaded.png"));

    await waitForKnowledgeIndexed(page);
    await screenshot(page, path.join(SCREENSHOT_DIR, "03-kb-indexed.png"));
  });

  test("04 knowledge base chat — input/output", async ({ page }) => {
    test.setTimeout(600_000);
    await startNewChat(page);
    await selectChatModel(page, MOCK_LLM_MODEL);
    await expect(page.getByText(MOCK_LLM_MODEL, { exact: false }).first()).toBeVisible({
      timeout: 30_000,
    });
    await attachKnowledgeCollection(page, KB_COLLECTION_NAME);
    await sendChatMessage(page, PROMPTS.kbCountTypes);
    await waitForAssistantReply(page, KB_ANSWER_HINTS);
    await screenshotChatExchange(page, path.join(SCREENSHOT_DIR, "04-kb-chat-answer.png"));
  });

  test("05 tool server registered in Open WebUI", async ({ page, request }) => {
    test.setTimeout(120_000);
    await registerToolServer(page, TOOL_SERVER_URL, request);
    await expect(
      page.getByText(/HW07 Netflix Tools|localhost:5005|host\.docker\.internal:5005|External Tool Servers/i).first(),
    ).toBeVisible({ timeout: 30_000 });
    await screenshot(page, path.join(SCREENSHOT_DIR, "05-tool-server-configured.png"));
  });

  test("06 live tool chat — country_info input/output", async ({ page }) => {
    test.setTimeout(600_000);
    await startNewChat(page);
    await selectChatModel(page, MOCK_LLM_MODEL);
    await enableToolsInChat(page);
    await sendChatMessage(page, PROMPTS.liveCountryCapital);
    await waitForToolInvocation(page, TOOL_OPERATION_HINTS);
    await waitForAssistantReply(page, TOOL_ANSWER_HINTS);
    await page.waitForTimeout(1500);
    await screenshotChatExchange(page, path.join(SCREENSHOT_DIR, "06-tool-chat-answer.png"));
  });
});
