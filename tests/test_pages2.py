from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://127.0.0.1:5000/")
    page.get_by_role("row", name="/ Old New", exact=True).get_by_role("link").nth(1).click()
    page.get_by_text("This page was generated on").click()
    page.locator("body").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
