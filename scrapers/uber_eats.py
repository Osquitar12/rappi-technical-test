from playwright.sync_api import sync_playwright
import pandas as pd
import json

DIRECCION = "C. Tlaxcoaque, Centro, Cuauhtémoc, 06080 Ciudad de México, CDMX, México"


def load_full_menu(page):

    print("Cargando menú completo...")

    previous = 0

    for _ in range(30):

        page.mouse.wheel(0, 6000)
        page.wait_for_timeout(2000)

        current = page.locator(
            '[data-testid^="store-item-"]'
        ).count()

        print(f"Productos visibles: {current}")

        if current == previous:
            break

        previous = current

    print("Menú cargado")


def extract_store_info(page):

    data = {
        "restaurant": "",
        "delivery_address": "",
        "restaurant_address": "",
        "eta": "",
        "delivery_fee": ""
    }

    try:
        data["restaurant"] = (
            page.locator("h1")
            .first
            .inner_text()
            .strip()
        )
    except:
        pass

    try:
        data["delivery_address"] = (
            page.locator(
                '[data-testid="delivery-address-label"]'
            )
            .inner_text()
            .strip()
        )
    except:
        pass

    spans = page.locator(
        'span[data-testid="rich-text"]'
    )

    total = spans.count()

    for i in range(total):

        try:

            text = (
                spans.nth(i)
                .inner_text()
                .strip()
            )

            if (
                "min" in text
                and not data["eta"]
            ):
                data["eta"] = text

            if (
                "Costo de envío" in text
                and not data["delivery_fee"]
            ):
                data["delivery_fee"] = text

            if (
                "Ciudad De México" in text
                and not data["restaurant_address"]
            ):
                data["restaurant_address"] = text

        except:
            pass

    return data


def extract_products(page):

    print("Extrayendo productos...")

    products = page.evaluate("""
    () => {

        const result = [];

        const cards = document.querySelectorAll(
            '[data-testid^="store-item-"]'
        );

        cards.forEach(card => {

            const rawText =
                card.innerText || "";

            const lines = rawText
                .split("\\n")
                .map(x => x.trim())
                .filter(Boolean);

            if (lines.length === 0)
                return;

            let name = "";
            let description = "";
            let current_price = "";
            let original_price = "";
            let discount = "";

            // ======================
            // NOMBRE
            // ======================

            for (const line of lines) {

                if (
                    !line.startsWith("$") &&
                    !line.includes("%")
                ) {

                    name = line;
                    break;
                }
            }

            // ======================
            // DESCRIPCION
            // ======================

            const desc1 =
                card.querySelector(
                    "span._ys"
                );

            if (desc1) {

                description =
                    desc1.innerText.trim();

            }

            if (!description) {

                const spans = [
                    ...card.querySelectorAll(
                        "span"
                    )
                ];

                for (const span of spans) {

                    const txt =
                        span.innerText.trim();

                    if (
                        txt.length > 5 &&
                        !txt.startsWith("$") &&
                        !txt.includes("%") &&
                        txt !== name
                    ) {

                        description = txt;
                        break;
                    }
                }
            }

            if (!description) {

                const elements = [
                    ...card.querySelectorAll(
                        "*"
                    )
                ];

                for (const el of elements) {

                    const txt =
                        el.innerText?.trim();

                    if (
                        txt &&
                        txt.length > 50 &&
                        !txt.startsWith("$") &&
                        !txt.includes("%") &&
                        txt !== name
                    ) {

                        description = txt;
                        break;
                    }
                }
            }

            // ======================
            // PRECIOS
            // ======================

            const prices =
                rawText.match(
                    /\\$\\d+\\.\\d+/g
                ) || [];

            if (prices.length >= 2) {

                current_price =
                    prices[0];

                original_price =
                    prices[1];

            }

            else if (
                prices.length === 1
            ) {

                current_price =
                    prices[0];

            }

            // ======================
            // DESCUENTO
            // ======================

            const discountMatch =
                rawText.match(
                    /-\\s*\\d+%/
                );

            if (discountMatch) {

                discount =
                    discountMatch[0];

            }

            // ======================
            // LIMPIEZA
            // ======================

            if (
                description === name
            ) {

                description = "";

            }

            result.push({

                name:
                    name,

                description:
                    description,

                current_price:
                    current_price,

                original_price:
                    original_price,

                discount:
                    discount

            });

        });

        return result;

    }
    """)

    print(
        f"Productos extraídos: {len(products)}"
    )

    return products

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        slow_mo=500
    )

    context = browser.new_context(
        viewport={
            "width": 1600,
            "height": 900
        }
    )

    page = context.new_page()

    print("Abriendo Uber Eats...")

    page.goto(
        "https://www.ubereats.com/mx",
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(5000)

    direccion_input = page.locator(
        "input"
    ).first

    direccion_input.click()

    direccion_input.fill(
        DIRECCION
    )

    page.wait_for_timeout(3000)

    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")

    print("Dirección seleccionada")

    page.wait_for_timeout(5000)

    buscador = page.locator(
        "input[placeholder*='Buscar']"
    ).first

    buscador.click()

    buscador.fill(
        "McDonald's"
    )

    page.wait_for_timeout(3000)

    page.keyboard.press("Enter")

    print("Buscando McDonald's...")

    page.wait_for_timeout(8000)

    enlaces = page.locator("a")

    total = enlaces.count()

    found = False

    for i in range(total):

        try:

            texto = enlaces.nth(i).inner_text(
                timeout=500
            )

            if "McDonald" in texto:

                print(
                    "Entrando:",
                    texto
                )

                enlaces.nth(i).click()

                found = True

                break

        except:
            pass

    if not found:

        print(
            "No se encontró McDonald's"
        )

        browser.close()
        raise SystemExit

    page.wait_for_timeout(8000)

    load_full_menu(page)

    store_info = extract_store_info(
        page
    )

    products = extract_products(
        page
    )

    result = {
        "platform": "Uber Eats",
        "searched_address": DIRECCION,
        **store_info,
        "products": products
    }

    with open(
        "ubereats_mcdonalds.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False
        )

    rows = []

    for product in products:

        rows.append({

            "platform":
                "Uber Eats",

            "searched_address":
                DIRECCION,

            "restaurant":
                store_info["restaurant"],

            "restaurant_address":
                store_info["restaurant_address"],

            "delivery_address":
                store_info["delivery_address"],

            "eta":
                store_info["eta"],

            "delivery_fee":
                store_info["delivery_fee"],

            "product":
                product["name"],

            "description":
                product["description"],

            "current_price":
                product["current_price"],

            "original_price":
                product["original_price"],

            "discount":
                product["discount"]
        })

    df = pd.DataFrame(rows)

    df.to_excel(
        "ubereats_mcdonalds.xlsx",
        index=False
    )

    print()
    print("=" * 50)
    print("SCRAPING FINALIZADO")
    print("=" * 50)

    print("Restaurante:", store_info["restaurant"])
    print("ETA:", store_info["eta"])
    print("Delivery Fee:", store_info["delivery_fee"])
    print("Productos:", len(products))

    print()
    print("JSON: ubereats_mcdonalds.json")
    print("Excel: ubereats_mcdonalds.xlsx")

    browser.close()