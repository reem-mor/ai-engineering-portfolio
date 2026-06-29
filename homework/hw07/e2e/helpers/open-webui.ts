import { expect, type Page } from "@playwright/test";

const OPEN_WEBUI_BASE = process.env.OPEN_WEBUI_URL ?? "http://localhost:3001";
export const MOCK_LLM_MODEL = process.env.OPEN_WEBUI_CHAT_MODEL ?? "hw07-mock-chat";
const MOCK_LLM_BASE = process.env.HW07_MOCK_LLM_URL ?? "http://localhost:8088/v1";

/** Dismiss first-run and release-note modals. */
export async function dismissModals(page: Page): Promise<void> {
  for (const label of [/okay, let's go!/i, /got it/i, /close toast/i]) {
    const btn = page.getByRole("button", { name: label });
    if (await btn.first().isVisible().catch(() => false)) {
      await btn.first().click().catch(() => undefined);
      await page.waitForTimeout(400);
    }
  }
}

/** Mask password/API fields before screenshots. */
export async function maskSensitiveFields(page: Page): Promise<void> {
  await page.evaluate(() => {
    document.querySelectorAll('input[type="password"], input[name*="key" i]').forEach((el) => {
      if (el instanceof HTMLInputElement) {
        el.value = "***";
        el.type = "password";
      }
    });
  });
}

export async function screenshot(page: Page, filePath: string): Promise<void> {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await maskSensitiveFields(page);
  await page.waitForLoadState("networkidle").catch(() => undefined);
  await page.waitForTimeout(1200);
  await page.screenshot({ path: filePath, fullPage: false });
}

/** Capture chat thread with user prompt + assistant reply visible. */
export async function screenshotChatExchange(page: Page, filePath: string): Promise<void> {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await maskSensitiveFields(page);
  await page.waitForTimeout(600);

  const logItems = page
    .locator('[aria-label="Chat Conversation"] listitem, [role="log"] listitem, [role="log"] > li');
  const count = await logItems.count();
  if (count >= 2) {
    const userItem = logItems.nth(count - 2);
    const assistantItem = logItems.nth(count - 1);
    await assistantItem.scrollIntoViewIfNeeded();
    await page.waitForTimeout(400);
    const userBox = await userItem.boundingBox();
    const assistantBox = await assistantItem.boundingBox();
    if (userBox && assistantBox) {
      const x = Math.max(0, Math.min(userBox.x, assistantBox.x) - 40);
      const y = Math.max(0, userBox.y - 24);
      const width = Math.min(1920 - x, Math.max(userBox.width, assistantBox.width) + 80);
      const height = Math.min(1080 - y, assistantBox.y + assistantBox.height - userBox.y + 48);
      await page.screenshot({
        path: filePath,
        clip: { x, y, width, height },
      });
      return;
    }
  }

  const conversation = page.locator('[aria-label="Chat Conversation"]').first();
  if (await conversation.isVisible().catch(() => false)) {
    await conversation.scrollIntoViewIfNeeded();
    await conversation.screenshot({ path: filePath });
    return;
  }

  await screenshot(page, filePath);
}

/** Point Open WebUI at the HW07 mock LLM (cloud CI fallback when Ollama chat segfaults). */
export async function configureMockLlmConnection(
  request: import("@playwright/test").APIRequestContext,
): Promise<void> {
  const signIn = await request.post(`${OPEN_WEBUI_BASE}/api/v1/auths/signin`, {
    data: { email: "admin@localhost.com", password: "admin" },
  });
  if (!signIn.ok()) {
    throw new Error(`Open WebUI sign-in failed: ${signIn.status()}`);
  }
  const { token } = (await signIn.json()) as { token: string };
  const headers = { Authorization: `Bearer ${token}` };

  await request.post(`${OPEN_WEBUI_BASE}/openai/config/update`, {
    headers,
    data: {
      ENABLE_OPENAI_API: true,
      OPENAI_API_BASE_URLS: [MOCK_LLM_BASE.replace(/\/$/, "")],
      OPENAI_API_KEYS: ["sk-hw07-mock"],
      OPENAI_API_CONFIGS: { "0": { enable: true } },
    },
  });

  const verify = await request.post(`${OPEN_WEBUI_BASE}/openai/verify`, {
    headers,
    data: { url: MOCK_LLM_BASE.replace(/\/$/, ""), key: "sk-hw07-mock" },
  });
  if (!verify.ok()) {
    const body = await verify.text();
    throw new Error(`Mock LLM verify failed (${verify.status()}): ${body}`);
  }
}

async function adminHeaders(
  request: import("@playwright/test").APIRequestContext,
): Promise<Record<string, string>> {
  const signIn = await request.post(`${OPEN_WEBUI_BASE}/api/v1/auths/signin`, {
    data: { email: "admin@localhost.com", password: "admin" },
  });
  if (!signIn.ok()) {
    throw new Error(`Open WebUI sign-in failed: ${signIn.status()}`);
  }
  const { token } = (await signIn.json()) as { token: string };
  return { Authorization: `Bearer ${token}` };
}

/** Remove prior chats so screenshot captures show a single clean exchange. */
export async function clearAllChats(
  request: import("@playwright/test").APIRequestContext,
): Promise<void> {
  const headers = await adminHeaders(request);
  await request.delete(`${OPEN_WEBUI_BASE}/api/v1/chats/`, { headers });
}

export async function gotoPath(page: Page, path: string): Promise<void> {
  await page.goto(`${OPEN_WEBUI_BASE}${path}`, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle").catch(() => undefined);
  await dismissModals(page);
  await ensureAuthenticated(page);
}

export async function gotoHome(page: Page): Promise<void> {
  await gotoPath(page, "/");
}

/** Sign in when auth is enabled (existing Open WebUI on :3000). Skipped when already in app. */
export async function ensureAuthenticated(page: Page): Promise<void> {
  const signIn = page.getByRole("button", { name: /^sign in$/i });
  if (!(await signIn.isVisible().catch(() => false))) {
    return;
  }
  const email = process.env.OPEN_WEBUI_EMAIL;
  const password = process.env.OPEN_WEBUI_PASSWORD;
  if (!email || !password) {
    throw new Error(
      "Open WebUI requires sign-in. Set OPEN_WEBUI_EMAIL and OPEN_WEBUI_PASSWORD, " +
        "or run scripts/start-stack.ps1 (WEBUI_AUTH=false on :3001).",
    );
  }
  await page.getByPlaceholder(/email/i).fill(email);
  await page.getByPlaceholder(/password/i).fill(password);
  await signIn.click();
  await page.waitForLoadState("networkidle").catch(() => undefined);
  await dismissModals(page);
}

export async function openWorkspaceKnowledge(page: Page): Promise<void> {
  await gotoPath(page, "/workspace/knowledge");
}

export async function createKnowledgeCollection(
  page: Page,
  name: string,
): Promise<void> {
  await gotoPath(page, "/workspace/knowledge/create");
  await page.getByPlaceholder(/Name your knowledge base|Knowledge Name/i).fill(name);
  await page
    .getByPlaceholder(/Describe your knowledge base|Knowledge Description/i)
    .fill("Netflix Kaggle dataset — 8,807 titles (TV Show + Movie) indexed for RAG chat");
  await page.getByRole("button", { name: /Create Knowledge/i }).click();
  await page.waitForURL(/\/workspace\/knowledge\//, { timeout: 60_000 });
  await expect(page.locator('input[type="file"]').first()).toBeAttached({ timeout: 30_000 });
}

const KB_DESCRIPTION_MARKER = "Netflix Kaggle dataset — 8,807 titles";

export async function openKnowledgeCollection(page: Page, name: string): Promise<void> {
  await openWorkspaceKnowledge(page);
  const marked = page.locator("div, a, button").filter({ hasText: KB_DESCRIPTION_MARKER }).first();
  if (await marked.isVisible().catch(() => false)) {
    await marked.click({ timeout: 30_000 });
  } else {
    await page.getByText(name, { exact: false }).first().click({ timeout: 30_000 });
  }
  await page.waitForURL(/\/workspace\/knowledge\/[a-f0-9-]+/i, { timeout: 30_000 });
  await page.waitForTimeout(800);
}

export async function uploadCsvToCollection(
  page: Page,
  csvPath: string,
  collectionName: string,
): Promise<void> {
  if (!(await page.locator('input[type="file"]').count())) {
    await openKnowledgeCollection(page, collectionName);
  }
  const fileInput = page.locator('input[type="file"]');
  if (await page.getByText("netflix_titles.csv", { exact: false }).isVisible().catch(() => false)) {
    return;
  }
  await fileInput.first().setInputFiles(csvPath);
  await expect(page.getByText("netflix_titles.csv", { exact: false })).toBeVisible({
    timeout: 60_000,
  });
}

export async function waitForKnowledgeIndexed(page: Page, timeoutMs = 300_000): Promise<void> {
  await expect(page.getByText(/netflix_titles\.csv/i).first()).toBeVisible({ timeout: 120_000 });

  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const fileRow = page.locator("button, div, li").filter({ hasText: /netflix_titles\.csv/i }).first();
    const rowText = (await fileRow.innerText().catch(() => "")).trim();
    const hasSize = /(MB|KB|GB)/i.test(rowText);
    const rowBusy = /uploading|processing|pending|spinner/i.test(rowText);

    if (hasSize && !rowBusy) {
      await page.waitForTimeout(20_000);
      return;
    }

    await page.waitForTimeout(5000);
    await page.reload({ waitUntil: "domcontentloaded" }).catch(() => undefined);
    await dismissModals(page);
  }

  const body = await page.locator("body").innerText();
  if (/netflix_titles\.csv[\s\S]{0,120}(MB|KB|GB)/i.test(body)) {
    return;
  }
  throw new Error("Knowledge base indexing did not complete in time");
}

export async function startNewChat(page: Page): Promise<void> {
  await gotoPath(page, "/");
  const newChat = page.getByRole("link", { name: /new chat/i }).or(page.getByRole("button", { name: /new chat/i }));
  if (await newChat.first().isVisible().catch(() => false)) {
    await newChat.first().click();
    await page.waitForURL(/\/(\?.*)?$/, { timeout: 15_000 }).catch(() => undefined);
  }
  await page.waitForTimeout(400);
  const logItems = page.getByRole("log").locator("listitem");
  const existing = await logItems.count().catch(() => 0);
  if (existing > 0) {
    await newChat.first().click({ force: true }).catch(() => undefined);
    await page.waitForTimeout(600);
  }
}

export async function attachKnowledgeCollection(page: Page, name: string): Promise<void> {
  const hashPrompt = page.getByText(/use '#' in the prompt/i);
  if (await hashPrompt.isVisible().catch(() => false)) {
    const input = page
      .locator("#chat-input")
      .or(page.locator('[contenteditable="true"]'))
      .or(page.getByPlaceholder(/send a message|message|ask|chat/i));
    await input.first().click();
    await input.first().fill(`#${name} `);
    return;
  }
  const attach = page.getByRole("button", { name: /knowledge|collection/i });
  if (await attach.first().isVisible().catch(() => false)) {
    await attach.first().click();
    await page.getByText(name, { exact: false }).first().click({ timeout: 15_000 });
  }
}

export async function selectChatModel(page: Page, modelName = MOCK_LLM_MODEL): Promise<void> {
  const preferred = modelName;
  const selector = page.getByRole("button", { name: /select a model/i });
  if (await selector.isVisible().catch(() => false)) {
    await selector.click();
    await page.getByText(preferred, { exact: false }).first().click({ timeout: 30_000 });
    await page.keyboard.press("Escape").catch(() => undefined);
    await page.waitForTimeout(500);
    return;
  }
  const current = page.getByText(/hw07-mock|nomic-embed-text|llama|qwen|gpt-oss/i).first();
  if (await current.isVisible().catch(() => false)) {
    await current.click();
    await page.getByText(preferred, { exact: false }).first().click({ timeout: 15_000 });
    await page.keyboard.press("Escape").catch(() => undefined);
  }
}

export async function sendChatMessage(page: Page, message: string): Promise<void> {
  const input = page
    .locator("#chat-input")
    .or(page.locator('[contenteditable="true"]'))
    .or(page.getByPlaceholder(/send a message|message|ask|chat/i))
    .or(page.locator("textarea").last());
  await input.first().click({ timeout: 30_000 });
  await input.first().fill(message);

  const sendCandidates = [
    page.getByRole("button", { name: /^send message$/i }),
    page.getByRole("button", { name: /^send$/i }),
    page.locator('button[type="submit"]'),
    page.locator('[data-testid="send-button"]'),
    page.locator('button[aria-label*="send" i]'),
  ];

  for (const candidate of sendCandidates) {
    if (await candidate.first().isVisible().catch(() => false)) {
      await candidate.first().click();
      await page.waitForTimeout(600);
      if (!(await messageStillInComposer(page, message))) {
        return;
      }
    }
  }

  // Open WebUI 0.10+: arrow button in composer toolbar (right of Voice Input)
  const voice = page.getByRole("button", { name: /voice input/i });
  if (await voice.isVisible().catch(() => false)) {
    const toolbar = voice.locator("xpath=ancestor::div[1]");
    const buttons = toolbar.locator("button");
    const count = await buttons.count();
    for (let i = count - 1; i >= 0; i -= 1) {
      const btn = buttons.nth(i);
      const label = ((await btn.getAttribute("aria-label")) ?? "").toLowerCase();
      if (label.includes("voice")) continue;
      await btn.click();
      await page.waitForTimeout(800);
      if (!(await messageStillInComposer(page, message))) {
        return;
      }
    }
  }

  await page.keyboard.press("Enter");
  await page.waitForTimeout(400);
  if (await messageStillInComposer(page, message)) {
    await page.keyboard.press("Control+Enter");
  }
}

async function messageStillInComposer(page: Page, message: string): Promise<boolean> {
  const snippet = message.slice(0, Math.min(24, message.length));
  const input = page
    .locator("#chat-input")
    .or(page.locator('[contenteditable="true"]'))
    .or(page.getByPlaceholder(/send a message|message|ask|chat/i))
    .or(page.locator("textarea").last());
  const text = await input.first().innerText().catch(() => "");
  return snippet.length > 0 && text.includes(snippet);
}

export async function waitForAssistantReply(
  page: Page,
  hints: RegExp[],
  timeoutMs = 300_000,
): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  const chatLocator = page
    .getByRole("log")
    .or(page.locator('[aria-label="Chat Conversation"]'))
    .or(page.locator("main"))
    .first();

  let lastText = "";
  let stablePolls = 0;

  while (Date.now() < deadline) {
    const stopButton = page.getByRole("button", { name: /stop|cancel/i });
    const isGenerating = await stopButton.first().isVisible().catch(() => false);

    const chatText = await chatLocator.innerText().catch(() => "");
    const bodyText = await page.locator("body").innerText().catch(() => "");
    const probe = chatText.length > 40 ? chatText : bodyText;

    if (!isGenerating && probe.length >= 20 && hints.some((h) => h.test(probe))) {
      if (probe === lastText) {
        stablePolls += 1;
      } else {
        stablePolls = 0;
        lastText = probe;
      }
      if (stablePolls >= 1) {
        return;
      }
    }

    await page.waitForTimeout(2000);
  }

  throw new Error(`Assistant reply did not match hints: ${hints.map(String).join(", ")}`);
}

/** Wait until Open WebUI surfaces a tool call panel (proves tool path, not memorized answer). */
export async function waitForToolInvocation(
  page: Page,
  hints: RegExp[],
  timeoutMs = 120_000,
): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const body = await page.locator("body").innerText();
    if (hints.some((h) => h.test(body))) {
      return;
    }
    await page.waitForTimeout(2000);
  }
  throw new Error(`Tool invocation UI did not appear: ${hints.map(String).join(", ")}`);
}

export async function registerToolServerViaApi(
  request: import("@playwright/test").APIRequestContext,
  url: string,
): Promise<void> {
  const signIn = await request.post(`${OPEN_WEBUI_BASE}/api/v1/auths/signin`, {
    data: { email: "admin@localhost.com", password: "admin" },
  });
  if (!signIn.ok()) {
    throw new Error(`Open WebUI sign-in failed: ${signIn.status()}`);
  }
  const { token } = (await signIn.json()) as { token: string };
  const headers = { Authorization: `Bearer ${token}` };

  const existing = await request.get(`${OPEN_WEBUI_BASE}/api/v1/configs/tool_servers`, { headers });
  if (existing.ok()) {
    const body = (await existing.json()) as { TOOL_SERVER_CONNECTIONS?: Array<{ url?: string }> };
    if (body.TOOL_SERVER_CONNECTIONS?.some((c) => (c.url ?? "").includes(url.replace(/\/$/, "")))) {
      return;
    }
  }

  const verify = await request.post(`${OPEN_WEBUI_BASE}/api/v1/configs/tool_servers/verify`, {
    headers,
    data: {
      url: url.replace(/\/$/, ""),
      path: "/openapi.json",
      type: "openapi",
      auth_type: "none",
      key: null,
      config: {},
    },
  });
  if (!verify.ok()) {
    throw new Error(`Tool server verify failed: ${await verify.text()}`);
  }

  const save = await request.post(`${OPEN_WEBUI_BASE}/api/v1/configs/tool_servers`, {
    headers,
    data: {
      TOOL_SERVER_CONNECTIONS: [
        {
          url: url.replace(/\/$/, ""),
          path: "/openapi.json",
          type: "openapi",
          auth_type: "none",
          key: null,
          config: {},
          info: {
            title: "HW07 Netflix Tools",
            description: "Live country and title lookups for HW07",
          },
        },
      ],
    },
  });
  if (!save.ok()) {
    throw new Error(`Tool server registration failed: ${await save.text()}`);
  }
}

export async function openToolSettings(page: Page): Promise<void> {
  await gotoPath(page, "/admin/settings/integrations");
  await expect(page.getByText(/External Tool Servers/i).first()).toBeVisible({ timeout: 30_000 });
}

export async function registerToolServer(
  page: Page,
  url: string,
  request?: import("@playwright/test").APIRequestContext,
): Promise<void> {
  if (request) {
    await registerToolServerViaApi(request, url);
  }
  await openToolSettings(page);
  await expect(page.getByText(url.replace(/\/$/, ""), { exact: false }).first()).toBeVisible({
    timeout: 30_000,
  });
}

export async function enableToolsInChat(page: Page): Promise<void> {
  const integrations = page.getByRole("button", { name: /integrations/i });
  if (await integrations.first().isVisible().catch(() => false)) {
    await integrations.first().click();
    const toolRow = page.getByText(/HW07 Netflix Tools|country_info/i).first();
    if (await toolRow.isVisible().catch(() => false)) {
      await toolRow.click();
    }
    await page.keyboard.press("Escape").catch(() => undefined);
  }
}
