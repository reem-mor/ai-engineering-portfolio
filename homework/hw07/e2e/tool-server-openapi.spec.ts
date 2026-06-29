import { test, expect } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TOOL_SERVER_BASE =
  process.env.TOOL_SERVER_BASE_URL ??
  process.env.TOOL_SERVER_URL ??
  "http://localhost:5005";

test.describe("HW07 tool server OpenAPI evidence", () => {
  test.beforeAll(async ({ request }) => {
    const health = await request.get(`${TOOL_SERVER_BASE.replace(/\/$/, "")}/health`).catch(() => null);
    test.skip(!health?.ok(), "Tool server not running on :5005");
  });

  test("capture OpenAPI docs page", async ({ page }) => {
    await page.goto(`${TOOL_SERVER_BASE.replace(/\/$/, "")}/docs`, { waitUntil: "networkidle" });
    await expect(page.getByText(/HW07 Netflix Tools|country_info|search_title/i).first()).toBeVisible({
      timeout: 30_000,
    });
    await page.screenshot({
      path: path.join(__dirname, "../screenshots/00-tool-server-openapi.png"),
      fullPage: true,
    });
  });
});
