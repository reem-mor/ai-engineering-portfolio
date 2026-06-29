import { test, expect } from "@playwright/test";

/**
 * E2E pipeline tests — backward build order (API → server → no Web UI required).
 *
 * Step 1: External API seam (mock RapidAPI via tool server)
 * Step 2: Local server endpoints (/health, /tools/*)
 * Step 3: Structured response contract for Open WebUI
 *
 * Full Web UI E2E (Step 4) lives in submission-screenshots.spec.ts (needs Docker + Ollama).
 */

const TOOL_BASE =
  process.env.TOOL_SERVER_BASE_URL ??
  process.env.TOOL_SERVER_URL ??
  "http://localhost:5005";

test.describe("HW07 E2E pipeline — API layer (Steps 1–3)", () => {
  test.beforeAll(async ({ request }) => {
    const health = await request.get(`${TOOL_BASE.replace(/\/$/, "")}/health`).catch(() => null);
    test.skip(!health?.ok(), "Tool server not running. Run scripts/start-stack.sh --mock-rapidapi");
  });

  test("Step 1 — RapidAPI seam returns live-shaped country data (mock)", async ({ request }) => {
    const response = await request.post(`${TOOL_BASE}/tools/country_info`, {
      data: { country_name: "Brazil" },
    });
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.ok).toBe(true);
    expect(body.source).toBe("mock");
    expect(body.data.capital).toMatch(/Brasília|Brasilia/i);
    expect(body.data.population).toBeGreaterThan(0);
  });

  test("Step 2 — Local server exposes OpenAPI tool contract", async ({ request }) => {
    const spec = await request.get(`${TOOL_BASE}/openapi.json`);
    expect(spec.ok()).toBeTruthy();
    const openapi = await spec.json();
    const ops = ["search_title", "country_info", "streaming_status"];
    for (const op of ops) {
      const found = Object.values(openapi.paths).some(
        (methods: Record<string, { operationId?: string }>) =>
          Object.values(methods).some((m) => m.operationId === op),
      );
      expect(found, `missing operationId ${op}`).toBe(true);
    }
  });

  test("Step 2 — search_title end-to-end through local server", async ({ request }) => {
    const response = await request.post(`${TOOL_BASE}/tools/search_title`, {
      data: { title: "Squid Game" },
    });
    expect(response.ok()).toBeTruthy();
    const body = await response.json();
    expect(body.ok).toBe(true);
    expect(body.data.results[0].title).toBe("Squid Game");
  });

  test("Step 2 — streaming_status validates country code at server", async ({ request }) => {
    const bad = await request.post(`${TOOL_BASE}/tools/streaming_status`, {
      data: { title: "Stranger Things", country_code: "USA" },
    });
    expect(bad.status()).toBe(422);

    const good = await request.post(`${TOOL_BASE}/tools/streaming_status`, {
      data: { title: "Stranger Things", country_code: "US" },
    });
    expect(good.ok()).toBeTruthy();
    expect((await good.json()).ok).toBe(true);
  });

  test("Step 3 — structured error when live key missing (no mock)", async ({ request }) => {
    test.skip(
      process.env.HW07_MOCK_RAPIDAPI !== "0",
      "Set HW07_MOCK_RAPIDAPI=0 and omit RAPIDAPI_KEY to test config errors",
    );
    const response = await request.post(`${TOOL_BASE}/tools/country_info`, {
      data: { country_name: "Brazil" },
    });
    const body = await response.json();
    expect(body.ok).toBe(false);
    expect(body.error).toMatch(/RAPIDAPI_KEY/i);
  });
});
