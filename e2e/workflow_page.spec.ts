import { test, expect } from "@playwright/test";
import { URL_STEM } from "./constants";

test('explore_workflow-page', async ({ page }) => {
  await page.goto(URL_STEM + 'workflows.html');
  await expect(page.locator('h1')).toContainText('Download stats for Bioconductor workflow packages');
  await page.getByRole('link', { name: 'Bioconductor annotation' }).click();
  await page.goto(URL_STEM + 'workflows.html');
  await expect(page.getByText('The number reported next to')).toBeVisible();
  await page.getByRole('link', { name: 'workflows_pkg_stats.tab' }).click();
  await page.goto(URL_STEM + 'workflows.html');
  await page.getByRole('link', { name: 'workflows_pkg_scores.tab' }).click();
  await page.goto(URL_STEM + 'workflows.html');
  await page.getByRole('link', { name: 'See Download stats for' }).click();
  await expect(page.locator('h1')).toContainText('Download stats for Bioconductor workflow repository (all packages combined)');
  await expect(page.locator('body')).toContainText('Back to the "Download stats for Bioconductor workflow packages"');
  await page.getByRole('link', { name: 'Back to the "Download stats' }).click();
});