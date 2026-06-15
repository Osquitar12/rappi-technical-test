from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    def handle_response(response):
        if "shop/index" in response.url:
            try:
                data = response.json()

                with open("didi_response.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                print("JSON capturado")
            except:
                pass

    page.on("response", handle_response)

    page.goto("https://www.didi-food.com")

    input("Presiona Enter cuando cargue el restaurante...")

    browser.close()