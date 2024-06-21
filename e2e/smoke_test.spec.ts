import { test, expect } from '@playwright/test';
import { TARGET_URL } from './constants';

test('Smoke Test', async ({ page }) => {
  await page.goto(TARGET_URL);
  await expect(page.getByRole('heading', { name: 'Download stats for' })).toBeVisible();
  await expect(page.locator('h1')).toContainText('Download stats for Bioconductor software packages');
  await page.getByRole('link', { name: 'Bioconductor annotation' }).click();
  await expect(page.locator('h1')).toContainText('Download stats for Bioconductor annotation packages');
  await page.getByRole('heading', { name: 'Download stats for' }).click();
  await expect(page.getByRole('heading', { name: 'Download stats for' })).toBeVisible();
  await page.getByRole('link', { name: 'Bioconductor workflow packages' }).click();
  await page.getByRole('heading', { name: 'Download stats for' }).click();
  await expect(page.locator('h1')).toContainText('Download stats for Bioconductor workflow packages');
  await expect(page.getByRole('heading', { name: 'Download stats for' })).toBeVisible();
  await page.getByRole('link', { name: 'Bioconductor annotation' }).click();
  await page.getByRole('heading', { name: 'Download stats for' }).click();
  await expect(page.getByRole('heading', { name: 'Download stats for' })).toBeVisible();
  await expect(page.locator('h1')).toContainText('Download stats for Bioconductor annotation packages');
});