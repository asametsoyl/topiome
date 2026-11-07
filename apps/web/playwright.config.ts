import { defineConfig, devices } from "@playwright/test";
import { tmpdir } from "node:os";
import { join } from "node:path";

const apiPort = 8011;
const webPort = 3011;
const apiUrl = `http://127.0.0.1:${apiPort}`;
const baseURL = `http://127.0.0.1:${webPort}`;
const runId = `${process.pid}`;
const databasePath = join(tmpdir(), `topiome-playwright-${runId}.sqlite`);
const storagePath = join(tmpdir(), `topiome-playwright-${runId}-storage`);

export default defineConfig({
  testDir: "./e2e",
  testIgnore: ["**/._*"],
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  reporter: "list",
  timeout: 10 * 60 * 1000,
  expect: { timeout: 15_000 },
  use: {
    ...devices["Desktop Chrome"],
    baseURL,
    trace: "retain-on-failure",
  },
  webServer: [
    {
      command: "uv run --extra dev uvicorn app.main:app --host 127.0.0.1 --port 8011",
      cwd: "../api",
      url: `${apiUrl}/api/v1/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        APP_ENV: "test",
        DATABASE_URL: `sqlite:///${databasePath}`,
        STORAGE_DIR: storagePath,
        APP_URL: baseURL,
        API_URL: apiUrl,
        CORS_ORIGINS: baseURL,
        QUEUE_MODE: "inline",
        AUTO_SEED: "true",
        ALLOW_DEMO_LOGIN: "true",
      },
    },
    {
      command: "npm run dev -- --hostname 127.0.0.1 --port 3011",
      cwd: ".",
      url: baseURL,
      reuseExistingServer: !process.env.CI,
      timeout: 180_000,
      env: { API_URL: apiUrl },
    },
  ],
});
