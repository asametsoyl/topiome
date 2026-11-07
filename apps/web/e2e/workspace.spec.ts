import { expect, test, type Page } from "@playwright/test";
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";

const publicGbmDir = process.env.TOPIOME_PUBLIC_GBM_DIR
  ? resolve(process.env.TOPIOME_PUBLIC_GBM_DIR)
  : undefined;
const publicGbmFiles = publicGbmDir
  ? [
      join(publicGbmDir, "GSM9744831_filtered_feature_bc_matrix_visium_primary.h5"),
      join(publicGbmDir, "GSM9744831_spatial_primary.tar.gz"),
    ]
  : [];

async function openDemo(page: Page) {
  await page.goto("/login");
  await page.getByRole("button", { name: "Explore the demo workspace" }).click();
  await expect(page).toHaveURL(/\/app$/);
}

async function createProject(page: Page, name: string, diseasePack: string) {
  await page.goto("/app/projects?new=1");
  const dialog = page.getByRole("dialog", { name: "New project" });
  await dialog.locator("input").fill(name);
  await dialog.locator("select").selectOption(diseasePack);
  const createResponse = page.waitForResponse(
    (response) => response.url().endsWith("/api/v1/projects") && response.request().method() === "POST",
  );
  await dialog.getByRole("button", { name: "Create project" }).click();
  const response = await createResponse;
  expect(response.status(), await response.text()).toBe(201);
  await expect(page).toHaveURL(/\/app\/projects\/[0-9a-f-]+$/i);
}

test("a researcher can create and complete a synthetic research run", async ({ page }) => {
  await openDemo(page);
  await page.goto("/app/projects");
  await page.getByRole("link", { name: /Breast cancer pilot/ }).click();
  await expect(page).toHaveURL(/\/app\/projects\/[0-9a-f-]+$/i);
  await page.getByRole("button", { name: "Add sample" }).click();
  const dialog = page.getByRole("dialog", { name: "Add a sample" });
  await dialog.locator("input").first().fill("E2E synthetic sample");
  await dialog.getByRole("button", { name: "Create demo sample" }).click();
  await expect(page).toHaveURL(/\/app\/samples\/[0-9a-f-]+$/i);
  await page.getByRole("button", { name: "Run analysis" }).click();
  await expect(page).toHaveURL(/\/app\/runs\/[0-9a-f-]+$/i);
  await expect(page.getByText("Completed", { exact: true })).toBeVisible({ timeout: 180_000 });
  const runId = page.url().split("/").at(-1);
  const run = await page.evaluate(async (id) => {
    const response = await fetch(`/api/v1/runs/${id}`);
    if (!response.ok) throw new Error(`Run API returned ${response.status}`);
    return response.json();
  }, runId);
  expect(run.status).toBe("succeeded");
  expect(run.summary.synthetic).toBe(true);
  expect(run.summary.n_spots).toBe(1200);
});

test("a public GSE331374 Visium sample uploads and completes through the UI", async ({ page }) => {
  test.skip(
    !publicGbmFiles.length || publicGbmFiles.some((file) => !existsSync(file)),
    "Set TOPIOME_PUBLIC_GBM_DIR to the local public GSE331374 sample directory.",
  );

  await openDemo(page);
  await createProject(page, `E2E GSE331374 ${Date.now()}`, "glioblastoma");
  await page.getByRole("button", { name: "Add sample" }).click();
  const dialog = page.getByRole("dialog", { name: "Add a sample" });
  await dialog.locator("input").first().fill("GSM9744831 primary GBM");
  await dialog.locator("input").nth(1).fill("GSM9744831");
  await dialog.locator("input").nth(2).fill("Primary glioblastoma");
  await dialog.locator('input[type="file"]').setInputFiles(publicGbmFiles);
  await dialog.getByRole("button", { name: "Upload sample" }).click();
  await expect(page).toHaveURL(/\/app\/samples\/[0-9a-f-]+$/i);
  await expect(page.getByText("GSM9744831_filtered_feature_bc_matrix_visium_primary.h5")).toBeVisible();
  await expect(page.getByText("GSM9744831_spatial_primary.tar.gz")).toBeVisible();
  await expect(page.getByText(/Research use only/i).first()).toBeVisible();

  await page.getByRole("button", { name: "Run analysis" }).click();
  await expect(page).toHaveURL(/\/app\/runs\/[0-9a-f-]+$/i);
  await expect(page.getByText("Completed", { exact: true })).toBeVisible({ timeout: 8 * 60_000 });
  const runId = page.url().split("/").at(-1);
  const run = await page.evaluate(async (id) => {
    const response = await fetch(`/api/v1/runs/${id}`);
    if (!response.ok) throw new Error(`Run API returned ${response.status}`);
    return response.json();
  }, runId);
  expect(run.status).toBe("succeeded");
  expect(run.disease_pack).toBe("glioblastoma");
  expect(run.provenance.input.kind).toBe("visium");
  expect(run.provenance.input.files).toHaveLength(2);
  expect(run.summary.n_spots).toBe(2930);
  const results = await page.evaluate(async (id) => {
    const response = await fetch(`/api/v1/runs/${id}/results`);
    if (!response.ok) throw new Error(`Results API returned ${response.status}`);
    return response.json();
  }, runId);
  const atlasCheck = results.payload.validation.atlas_check;
  expect(atlasCheck.status).toBe("ok");
  expect(atlasCheck.diagonal_mean).toBeLessThan(0.2);
  expect(atlasCheck.top1_accuracy).toBe(0);
  expect(results.payload.warnings).toContain(
    "Predicted zones correspond weakly to the external atlas (Ivy Glioblastoma Atlas Project (ISH)); zone labels are low-confidence.",
  );
});
