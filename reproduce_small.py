from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 320, 'height': 568})
    page = context.new_page()
    page.goto("http://localhost:5000")
    page.wait_for_load_state("networkidle")

    page.screenshot(path="mobile_small_view.png")

    widget = page.locator(".floating-widget")
    if widget.is_visible():
        print("Widget visible on small screen")
    else:
        print("Widget NOT visible on small screen")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
