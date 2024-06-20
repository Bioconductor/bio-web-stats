import { test, expect } from '@playwright/test';
import { TARGET_URL } from './constants';

test('Smoke Test', async ({ page }) => {
  await page.goto(TARGET_URL);

  // Expect a title "to contain" a substring.
  // TODO establish stable database for e2e tests
  await expect(page).toHaveTitle(/Download stats for Bioconductor software packages/);
  await expect(page.getByText('See download stats for:')).toBeVisible();
  await page.getByRole('link', { name: 'Bioconductor annotation' }).click();
  await expect(page.locator('h1')).toContainText('Download stats for Bioconductor annotation packages');
  await expect(page.getByRole('link', { name: 'Bioconductor software packages' })).toBeVisible();
  await page.getByRole('link', { name: 'Bioconductor experiment' }).click();
  await expect(page.locator('h1')).toContainText('Download stats for Bioconductor experiment packages');
  await page.getByRole('link', { name: 'Bioconductor software packages' }).click();
  await page.locator('p').filter({ hasText: 'affy (8036)' }).getByRole('link').click();
  await expect(page.locator('h1')).toContainText('Download stats for software package affy');
  await page.getByText('Number of package downloads').click();
  await expect(page.locator('body')).toContainText('Number of package downloads from the Bioconductor software package repository, year by year, from 2024 back to 2009 (years with no downloads are omitted):');
  await page.getByRole('link', { name: 'affy_2024_stats.tab' }).click();
  await expect(page.locator('pre')).toContainText('Year Month Nb_of_distinct_IPs Nb_of_downloads 2024 Jan 7236 17066 2024 Feb 8301 12473 2024 Mar 4181 7386 2024 Apr 0 0 2024 May 0 0 2024 Jun 0 0 2024 Jul 0 0 2024 Aug 0 0 2024 Sep 0 0 2024 Oct 0 0 2024 Nov 0 0 2024 Dec 0 0 2024 all 17569 36925');
});

