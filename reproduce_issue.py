from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    # Use iPhone 12 Pro dimensions
    context = browser.new_context(viewport={'width': 390, 'height': 844}, user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1')
    page = context.new_page()
    page.goto("http://localhost:5000")

    # Wait for the page to load
    page.wait_for_load_state("networkidle")

    # Take screenshot of the whole page
    page.screenshot(path="mobile_view.png")

    # Check if the widget is visible
    # The widget has class .floating-widget
    widget = page.locator(".floating-widget")

    if widget.is_visible():
        print("Widget is visible")
        # Take a screenshot of the widget specifically
        widget.screenshot(path="widget.png")
    else:
        print("Widget is NOT visible")
        # Check if it is in the DOM
        if widget.count() > 0:
            print("Widget is in DOM but hidden")
            # Check bounding box
            box = widget.bounding_box()
            print(f"Bounding box: {box}")

            # Check CSS properties
            display = widget.evaluate("element => window.getComputedStyle(element).display")
            opacity = widget.evaluate("element => window.getComputedStyle(element).opacity")
            visibility = widget.evaluate("element => window.getComputedStyle(element).visibility")
            z_index = widget.evaluate("element => window.getComputedStyle(element).zIndex")
            print(f"CSS - Display: {display}, Opacity: {opacity}, Visibility: {visibility}, zIndex: {z_index}")
        else:
            print("Widget is NOT in DOM")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
