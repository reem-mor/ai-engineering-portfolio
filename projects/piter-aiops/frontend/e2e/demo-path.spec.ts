import { test, expect, type Page } from "@playwright/test";

const baseURL = process.env.PITER_BASE_URL || "http://127.0.0.1:8080";

async function requireDemoPolishUi(page: Page): Promise<void> {
  const marker = page.locator('.app-shell[data-ui-version="demo-polish-v1"]');
  const hasMarker = await marker.isVisible().catch(() => false);
  test.skip(
    !hasMarker,
    "Built demo-polish SPA not served — run: cd frontend && npm run build, then restart Flask on " +
      baseURL,
  );
}

async function clickStartAlertStream(page: Page): Promise<void> {
  const startBtn = page.locator(".top-bar-actions button.btn-primary", {
    hasText: /start alert stream/i,
  });
  await expect(startBtn).toBeVisible({ timeout: 10_000 });
  await startBtn.click();
}

test.describe("PITER demo path", () => {
  test.beforeEach(async ({ request }) => {
    try {
      const res = await request.get(`${baseURL}/api/health`);
      test.skip(!res.ok(), "Server not running at " + baseURL);
    } catch {
      test.skip(true, "Server not reachable at " + baseURL);
    }
  });

  test("SPA shell loads", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator(".app-shell")).toBeVisible();
    await expect(page.getByText("Operations Dashboard")).toBeVisible();
    await requireDemoPolishUi(page);
    await expect(page.locator(".top-bar-actions button.btn-primary")).toBeVisible();
  });

  test("alert stream increments and P1 moment appears", async ({ page }) => {
    await page.goto("/");
    await requireDemoPolishUi(page);
    await clickStartAlertStream(page);
    await expect(page.locator(".stream-counter")).toBeVisible({ timeout: 5000 });
    await expect(page.locator(".stream-counter")).not.toHaveText("Alerts: 0", { timeout: 8000 });
    const p1Moment = page
      .locator(".app-shell.critical-mode, .p1-modal, .alert-banner-critical")
      .first();
    await expect(p1Moment).toBeVisible({ timeout: 30_000 });
  });

  test("analyze CTA visible after P1", async ({ page }) => {
    await page.goto("/");
    await requireDemoPolishUi(page);
    await clickStartAlertStream(page);
    const analyzeBtn = page.getByRole("button", { name: /analyze p1 incident/i });
    await expect(analyzeBtn.first()).toBeVisible({ timeout: 30_000 });
  });

  test("chat dock opens without horizontal overflow", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto("/");
    await requireDemoPolishUi(page);
    const shell = page.locator(".app-shell");
    await expect(shell).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    expect(overflow).toBe(false);
    await expect(page.locator(".chat-dock, .chat-dock-collapsed")).toBeVisible();
  });
});
