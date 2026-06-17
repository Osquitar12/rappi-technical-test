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
    page.wait_for_load_state("networkidle")
    print("🔥 Página cargada")

    # =========================
    # 1. DIRECCIÓN
    # =========================
    page.click("text=Entrega")
    page.wait_for_timeout(3000)

    address_input = page.locator("input:visible").first
    address_input.click()
    address_input.press("Control+A")
    address_input.press("Delete")
    address_input.type(address, delay=120)

    print("⌨️ Dirección escrita")
    page.wait_for_timeout(5000)

    candidatos = page.locator("li:visible, [role='option']:visible")
    total = candidatos.count()
    print(f"📍 Sugerencias encontradas: {total}")

    if total > 0:
        candidatos.first.click()
        print("✅ Primera sugerencia seleccionada")
    else:
        options = page.locator("li.el-select-dropdown__item")
        for i in range(options.count()):
            opt = options.nth(i)
            try:
                if opt.is_visible():
                    opt.click()
                    print("📍 Dirección seleccionada (fallback)")
                    break
            except:
                continue

    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)
    print(f"📌 URL tras dirección: {page.url}")

    # =========================
    # 2. BUSCAR McDONALD'S
    # =========================
    # Guardar URL antes de abrir buscador para detectar el nuevo input
    url_before_search = page.url

    # Abrir buscador
    try:
        page.locator("text=Buscar comidas").first.click(timeout=3000)
    except:
        try:
            page.locator("text=Buscar").first.click(timeout=3000)
        except:
            page.locator("[aria-label*='Buscar']").first.click()

    print("🔍 Buscador abierto")
    page.wait_for_timeout(2000)

    # --- FIX PRINCIPAL ---
    # Buscar el input de búsqueda con selectores específicos, excluyendo el de dirección
    # Intentamos en orden de especificidad
    search_box = None

    selectors_to_try = [
        "input[type='search']",
        "input[placeholder*='Buscar']",
        "input[placeholder*='buscar']",
        "input[placeholder*='restaurante']",
        "input[placeholder*='comida']",
        ".search-input input",
        ".search-bar input",
        "header input",
        "[class*='search'] input",
    ]

    for sel in selectors_to_try:
        try:
            el = page.locator(sel).first
            el.wait_for(state="visible", timeout=2000)
            search_box = el
            print(f"✅ Input de búsqueda encontrado con: {sel}")
            break
        except:
            continue

    # Último recurso: tomar el input que NO sea el de dirección
    if search_box is None:
        print("⚠️ Usando fallback: segundo input visible")
        all_inputs = page.locator("input:visible")
        count_inputs = all_inputs.count()
        print(f"   Inputs visibles: {count_inputs}")
        for i in range(count_inputs):
            inp = all_inputs.nth(i)
            placeholder = inp.get_attribute("placeholder") or ""
            val = inp.input_value() or ""
            print(f"   input[{i}] placeholder='{placeholder}' value='{val[:30]}'")
            # Saltar si ya tiene la dirección escrita
            if address[:10] in val or "Tlaxcoaque" in val:
                continue
            search_box = inp
            print(f"   → Usando input[{i}]")
            break

    if search_box is None:
        raise Exception("❌ No se encontró el input de búsqueda")

    search_box.click()
    search_box.fill("")
    search_box.type("McDonalds", delay=80)
    page.keyboard.press("Enter")

    print("🔎 Buscando McDonalds...")
    page.wait_for_timeout(4000)

    # =========================
    # 3. CLICK RESTAURANTE
    # =========================
    first_restaurant = page.locator("dl.shop-card").first
    first_restaurant.wait_for(state="attached", timeout=10000)
    first_restaurant.scroll_into_view_if_needed()
    page.wait_for_timeout(1000)

    url_before_click = page.url
    first_restaurant.click()
    print("🍔 Entrando al primer McDonald's")

    # =========================
    # 4. VERIFICAR NAVEGACIÓN
    # =========================
    try:
        page.wait_for_function(
            f"() => window.location.href !== '{url_before_click}'",
            timeout=8000
        )
        print(f"✅ Navegó a: {page.url}")
    except:
        print(f"⚠️ La URL no cambió, sigue en: {page.url}")
        page.screenshot(path="debug_after_click.png")

    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # =========================
    # 5. EXTRACCIÓN INFO RESTAURANTE
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
    # 6. EXTRACCIÓN PRODUCTOS
    # =========================
    products = []
    print(f"📦 Extrayendo {count} productos...")

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
                discount = (
                    soup.select_one("[class*='discount']") or
                    soup.select_one("[class*='promo']") or
                    soup.select_one("[class*='tag']")
                )

            products.append({
                "name":           name.get_text(strip=True)     if name     else "",
                "description":    desc.get_text(strip=True)     if desc     else "",
                "current_price":  price.get_text(strip=True)    if price    else "",
                "original_price": original.get_text(strip=True) if original else "",
                "discount":       discount.get_text(strip=True) if discount else "",
            })

        except Exception as e:
            continue

    print(f"✅ {len(products)} productos extraídos")

    # =========================
    # 7. GUARDAR RESULTADOS
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