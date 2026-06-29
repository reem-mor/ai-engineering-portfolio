import { test, expect } from "@playwright/test";
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
  createKnowledgeCollection,
  dismissModals,
  enableToolsInChat,
  registerToolServer,
  screenshot,
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
const STACK_START_HINT =
  process.platform === "win32"
    ? "Run scripts/start-stack.ps1"
    : "Run scripts/start-stack.sh";

test.describe("HW07 submission screenshots", () => {
  test.beforeAll(async ({ request }) => {
    const [webui, tools] = await Promise.all([
      request.get(OPEN_WEBUI_URL).catch(() => null),
      request.get(TOOL_SERVER_HEALTH).catch(() => null),
    ]);
    test.skip(!webui?.ok(), `Open WebUI not running at ${OPEN_WEBUI_URL}. ${STACK_START_HINT}`);
    test.skip(!tools?.ok(), `Tool server not running. ${STACK_START_HINT}`);
    const health = await tools!.json();
    expect(health.status).toBe("ok");
  });

  test("capture submission screenshots 01-06", async ({ page }) => {
    test.setTimeout(900_000);

    await page.goto(`${OPEN_WEBUI_URL}/workspace/knowledge/create`, { waitUntil: "domcontentloaded" });
    await dismissModals(page);
    await createKnowledgeCollection(page, KB_COLLECTION_NAME);
    await screenshot(page, path.join(SCREENSHOT_DIR, "01-kb-collection-created.png"));

    await uploadCsvToCollection(page, CSV_PATH, KB_COLLECTION_NAME);
    await screenshot(page, path.join(SCREENSHOT_DIR, "02-kb-csv-uploaded.png"));

    await waitForKnowledgeIndexed(page);
    await screenshot(page, path.join(SCREENSHOT_DIR, "03-kb-indexed.png"));

    await startNewChat(page);
    await selectChatModel(page);
    await attachKnowledgeCollection(page, KB_COLLECTION_NAME);
    await sendChatMessage(page, PROMPTS.kbCountTypes);
    await waitForAssistantReply(page, KB_ANSWER_HINTS);
    await screenshot(page, path.join(SCREENSHOT_DIR, "04-kb-chat-answer.png"));

    await registerToolServer(page, TOOL_SERVER_URL);
    await expect(
      page.getByText(/HW07 Netflix Tools|host\.docker\.internal:5005|Manage Tool Servers/i).first(),
    ).toBeVisible({ timeout: 30_000 });
    await screenshot(page, path.join(SCREENSHOT_DIR, "05-tool-server-configured.png"));

    await enableToolsInChat(page);
    await sendChatMessage(page, PROMPTS.liveCountryCapital);
    await waitForToolInvocation(page, TOOL_OPERATION_HINTS);
    await waitForAssistantReply(page, TOOL_ANSWER_HINTS);
    await screenshot(page, path.join(SCREENSHOT_DIR, "06-tool-chat-answer.png"));
  });
});
