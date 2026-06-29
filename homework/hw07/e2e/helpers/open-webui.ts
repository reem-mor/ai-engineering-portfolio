import { expect, type Page } from "@playwright/test";

const OPEN_WEBUI_BASE = process.env.OPEN_WEBUI_URL ?? "http://localhost:3001";

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
  await maskSensitiveFields(page);
  await page.waitForTimeout(800);
  await page.screenshot({ path: filePath, fullPage: true });
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
  await page.getByPlaceholder("Name your knowledge base").fill(name);
  await page
    .getByPlaceholder("Describe your knowledge base and objectives")
    .fill("Netflix titles CSV knowledge base for HW07");
  await page.getByRole("button", { name: "Create Knowledge", exact: true }).click();
  await page.waitForURL(/\/workspace\/knowledge\//, { timeout: 60_000 });
  await expect(page.locator('input[type="file"]').first()).toBeAttached({ timeout: 30_000 });
}

const KB_DESCRIPTION_MARKER = "Netflix titles CSV knowledge base for HW07";

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

export async function ensureKnowledgeCollection(page: Page, name: string): Promise<void> {
  await openWorkspaceKnowledge(page);
  const marked = page.locator("div, a, button").filter({ hasText: KB_DESCRIPTION_MARKER }).first();
  if (await marked.isVisible().catch(() => false)) {
    await marked.click();
    await page.waitForURL(/\/workspace\/knowledge\/[a-f0-9-]+/i, { timeout: 30_000 });
    return;
  }
  await createKnowledgeCollection(page, name);
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

export async function waitForKnowledgeIndexed(page: Page, timeoutMs = 120_000): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const body = await page.locator("body").innerText();
    if (/netflix_titles\.csv/i.test(body)) {
      if (/(indexed|processed|ready|completed|chunks|embed|vector)/i.test(body)) {
        return;
      }
      if (!/uploading|processing|pending/i.test(body)) {
        return;
      }
    }
    await page.waitForTimeout(4000);
    await page.reload({ waitUntil: "domcontentloaded" }).catch(() => undefined);
    await dismissModals(page);
  }
  if (/netflix_titles\.csv/i.test(await page.locator("body").innerText())) {
    return;
  }
  throw new Error("Knowledge base indexing did not complete in time");
}

export async function startNewChat(page: Page): Promise<void> {
  await gotoPath(page, "/");
  const newChat = page.getByRole("button", { name: /new chat/i });
  if (await newChat.first().isVisible().catch(() => false)) {
    await newChat.first().click();
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

export async function selectChatModel(page: Page): Promise<void> {
  const preferred = process.env.OPEN_WEBUI_CHAT_MODEL ?? "llama3.2:3b";
  const current = page.getByText(/nomic-embed-text|llama|qwen|gpt-oss/i).first();
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
  const send = page.getByRole("button", { name: /^send$/i }).or(page.locator('button[type="submit"]'));
  if (await send.first().isVisible().catch(() => false)) {
    await send.first().click();
  } else {
    await page.keyboard.press("Enter");
  }
}

export async function waitForAssistantReply(
  page: Page,
  hints: RegExp[],
  timeoutMs = 180_000,
): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  const assistantMessages = page.locator(
    [
      '[data-testid="chat-message-assistant"]',
      '.chat-assistant',
      '[class*="assistant-message"]',
      'div[class*="group"][class*="assistant"]',
    ].join(", "),
  );

  let lastText = "";
  let stablePolls = 0;

  while (Date.now() < deadline) {
    const stopButton = page.getByRole("button", { name: /stop|cancel/i });
    const isGenerating = await stopButton.first().isVisible().catch(() => false);

    const count = await assistantMessages.count();
    if (count > 0 && !isGenerating) {
      const latest = assistantMessages.nth(count - 1);
      const text = (await latest.innerText()).trim();

      if (text.length >= 25 && hints.some((h) => h.test(text))) {
        if (text === lastText) {
          stablePolls += 1;
        } else {
          stablePolls = 0;
          lastText = text;
        }

        if (stablePolls >= 2) {
          return;
        }
      } else {
        stablePolls = 0;
        lastText = text;
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

export async function openToolSettings(page: Page): Promise<void> {
  await gotoPath(page, "/admin/settings/tools");
  await expect(page.getByText("Manage Tool Servers")).toBeVisible({ timeout: 30_000 });
}

export async function registerToolServer(page: Page, url: string): Promise<void> {
  await openToolSettings(page);
  const existing = page.getByText(url, { exact: false });
  if ((await existing.count()) > 0) {
    return;
  }
  await page.getByText("Manage Tool Servers").locator("..").locator("button").first().click();
  const dialog = page.getByRole("dialog");
  await dialog.getByPlaceholder("API Base URL").fill(url);
  await dialog.getByPlaceholder("Enter name").fill("HW07 Netflix Tools");
  await dialog.getByPlaceholder("Enter description").fill("Live country and title lookups for HW07");
  await dialog.getByRole("button", { name: "Save" }).click();
  await page.waitForTimeout(1000);
  await page.getByRole("button", { name: /^Save$/ }).click();
  await expect(page.getByText("Connections saved successfully")).toBeVisible({ timeout: 30_000 });
}

export async function enableToolsInChat(page: Page): Promise<void> {
  await startNewChat(page);
  await selectChatModel(page);
  const toolsToggle = page.getByRole("button", { name: /tools|plugin/i });
  if (await toolsToggle.first().isVisible().catch(() => false)) {
    await toolsToggle.first().click();
  }
}
