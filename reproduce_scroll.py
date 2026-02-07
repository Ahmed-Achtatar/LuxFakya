from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    # Use iPhone 12 Pro dimensions
    context = browser.new_context(viewport={'width': 390, 'height': 844}, user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1')
    page = context.new_page()
    page.goto("http://localhost:5000")

    # Wait for the page to load
    page.wait_for_load_state("networkidle")

    # Scroll down to the bottom
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000) # Wait for potential animations

    # Take screenshot of the bottom
    page.screenshot(path="mobile_view_bottom.png")

    # Check if the widget is visible
    widget = page.locator(".floating-widget")

    if widget.is_visible():
        print("Widget is visible at bottom")
        widget.screenshot(path="widget_bottom.png")
    else:
        print("Widget is NOT visible at bottom")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
