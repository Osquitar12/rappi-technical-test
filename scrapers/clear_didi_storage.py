from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir="didi_profile",
        headless=False
    )

    page = context.new_page()
    page.goto("https://www.didi-food.com/es-MX/food/")

    # limpiar storage del sitio
    page.evaluate("localStorage.clear()")
    page.evaluate("sessionStorage.clear()")

    print("🧹 Storage limpiado (puede que aún quede cookie)")

    
    context.close()