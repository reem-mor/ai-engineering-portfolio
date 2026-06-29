import { defineConfig } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  testDir: ".",
  fullyParallel: false,
  workers: 1,
  timeout: 300_000,
  expect: { timeout: 120_000 },
  use: {
    baseURL: process.env.OPEN_WEBUI_URL ?? "http://localhost:3001",
    viewport: { width: 1920, height: 1080 },
    screenshot: "off",
    trace: "retain-on-failure",
  },
  outputDir: path.join(__dirname, "test-results"),
  reporter: [["list"]],
});
