from playwright.sync_api import sync_playwright, expect
import time

def verify_luxfakia():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Go to home
        print("Navigating to home...")
        page.goto("http://127.0.0.1:5000/")
        expect(page).to_have_title("LuxFakia - Premium Dates & Nuts")

        # Take screenshot of home
        page.screenshot(path="verification/home.png", full_page=True)
        print("Home screenshot taken.")

        # Go to Shop
        print("Navigating to shop...")
        page.click("text=Shop")
        expect(page).to_have_url("http://127.0.0.1:5000/shop")

        # Take screenshot of shop
        page.screenshot(path="verification/shop.png", full_page=True)
        print("Shop screenshot taken.")

        browser.close()

if __name__ == "__main__":
    verify_luxfakia()
