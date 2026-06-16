from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir="didi_profile",
        headless=False
    )

    page = context.new_page()
    page.goto("https://www.didi-food.com/es-MX/food/")

    print("\n👉 Haz login manual en el navegador")
    input("Cuando termines el login, presiona ENTER aquí...")

    print("🔥 Sesión guardada correctamente en 'didi_profile'")

    context.close()