import { test, expect } from '@playwright/test';
import { TARGET_URL } from './constants';

test('has title', async ({ page }) => {
  await page.goto(TARGET_URL);

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Download stats for Bioconductor software packages/);
});
