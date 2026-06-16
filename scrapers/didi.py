from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import pandas as pd

address = "C. Tlaxcoaque, Centro, Cuauhtémoc, 06080 Ciudad de México, CDMX, México"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir="didi_profile",
        headless=False,
        args=["--start-maximized"]
    )

    page = context.new_page()
    page.goto("https://www.didi-food.com/es-MX/food/")

    print("🔥 Iniciando...")

    # =========================
    # 1. DIRECCIÓN
    # =========================
    page.click("text=Entrega")

    address_input = page.locator("input").first
    address_input.click()
    address_input.fill(address)
    page.wait_for_timeout(1500)

    options = page.locator("li.el-select-dropdown__item")
    for i in range(options.count()):
        opt = options.nth(i)
        try:
            if opt.is_visible():
                opt.click()
                print("📍 Dirección seleccionada")
                break
        except:
            continue

    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # =========================
    # 2. BUSCAR
    # =========================
    try:
        page.locator("text=Buscar comidas").first.click(timeout=3000)
    except:
        try:
            page.locator("text=Buscar").first.click(timeout=3000)
        except:
            page.locator("[aria-label*='Buscar']").first.click()

    page.wait_for_timeout(1000)

    search_box = page.locator("input").first
    search_box.click()
    search_box.fill("McDonalds")
    page.keyboard.press("Enter")

    page.wait_for_timeout(4000)

    # =========================
    # 3. CLICK RESTAURANTE
    # =========================
    first_restaurant = page.locator("dl.shop-card").first
    first_restaurant.wait_for(state="attached", timeout=10000)
    first_restaurant.scroll_into_view_if_needed()
    page.wait_for_timeout(1000)

    url_before = page.url
    first_restaurant.click()

    # =========================
    # 4. VERIFICAR NAVEGACIÓN
    # =========================
    try:
        page.wait_for_function(
            f"() => window.location.href !== '{url_before}'",
            timeout=8000
        )
    except:
        page.screenshot(path="debug_after_click.png")

    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # =========================
    # 5. EXTRACCIÓN
    # =========================
    items = page.locator("div.shop_item")
    count = items.count()

    restaurant_name = "N/A"
    for sel in ["h1.shop-name", ".shop-name", "h1"]:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                restaurant_name = el.inner_text(timeout=2000)
                break
        except:
            continue

    eta, delivery_fee = "N/A", "N/A"
    try:
        eta = page.locator("li.service-item").nth(0).inner_text(timeout=2000)
        delivery_fee = page.locator("li.service-item").nth(1).inner_text(timeout=2000)
    except:
        pass

    # =========================
    # 6. PRODUCTOS
    # =========================
    products = []

    for i in range(count):
        item = items.nth(i)
        try:
            html = item.inner_html(timeout=1000)
            soup = BeautifulSoup(html, "html.parser")

            name     = soup.select_one("p.title")
            desc     = soup.select_one("p.desc")
            price    = soup.select_one("span.price")
            original = soup.select_one("s.crossed-price")
            discount = soup.select_one("p.tips")

            if not price or not price.get_text(strip=True):
                price = soup.select_one("[class*='price']")

            if not discount or not discount.get_text(strip=True):
                discount = soup.select_one("[class*='discount']") or \
                           soup.select_one("[class*='promo']") or \
                           soup.select_one("[class*='tag']")

            products.append({
                "name":           name.get_text(strip=True)     if name     else "",
                "description":    desc.get_text(strip=True)     if desc     else "",
                "current_price":  price.get_text(strip=True)    if price    else "",
                "original_price": original.get_text(strip=True) if original else "",
                "discount":       discount.get_text(strip=True) if discount else "",
            })

        except:
            continue

    # =========================
    # 7. GUARDAR
    # =========================
    result = {
        "restaurant":   restaurant_name,
        "eta":          eta,
        "delivery_fee": delivery_fee,
        "products":     products
    }

    with open("resultado_mcdonalds.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("💾 Guardado en resultado_mcdonalds.json")

    df = pd.DataFrame(products)
    df.insert(0, "restaurant", restaurant_name)
    df.insert(1, "eta", eta)
    df.insert(2, "delivery_fee", delivery_fee)

    df.to_excel("resultado_mcdonalds.xlsx", index=False)
    print("📊 Guardado en resultado_mcdonalds.xlsx")

    context.close()