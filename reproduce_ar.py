from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 390, 'height': 844})
    page = context.new_page()

    # Set language to AR
    page.goto("http://localhost:5000/set_lang/ar")
    page.wait_for_load_state("networkidle")

    # Now check the homepage
    page.goto("http://localhost:5000")
    page.wait_for_load_state("networkidle")

    page.screenshot(path="mobile_view_ar.png")

    widget = page.locator(".floating-widget")
    if widget.is_visible():
        print("Widget visible in AR")
        widget.screenshot(path="widget_ar.png")
    else:
        print("Widget NOT visible in AR")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
