import json
import csv
import requests

TOKEN = "ft.gAAAAABqL-ofawQJOwat06F-R3GdcweiX3XN44HCfGTa9c0EfUpbGMDucYSZyCk4WUDL7XMqqyFUYBfkrOdv8D_pj3EpSJvA1jpbPg8vWLlE5ojtjyZfDfqoTOR6geBDuxV7A2GxpZ_0wtFMHkojDPHd4is40H0jnxUbSNAF1nFMA3pcMkerqvaYLYFlaRfS08oQvaj8v5BZUn32sZWUlFo_DYCaWjRh15CK_ijvI_XzfBXLVfC0AiS8Ha7AVqU1y36LWlSAtKnY2y1F7gQuHf1blMzCCy6W-LKVMSZ_lwCUw5sw9Vm1qnXdzgMJaQHycVjzvIU18ZKftrdLwm3yevl1fbUg_i6MRgxwkCOC6CcEdUM2Y3Szsw4_eCJqslShdyzDUnpcu_6FYUC2t5GURSATsVyOVa31Lg=="
DEVICE_ID = "f763276f-bcfa-4bcc-b6d7-b3c29016e11fR"

STORE_ID = "1306705702"

URL = f"https://services.mxgrability.rappi.com/api/web-gateway/web/restaurants-bus/store/id/{STORE_ID}/"

headers = {
    "accept": "application/json",
    "accept-language": "es-MX",
    "app-version": "1.162.2",
    "app-version-name": "1.162.2",
    "authorization": f"Bearer {TOKEN}",
    "content-type": "application/json; charset=UTF-8",
    "deviceid": DEVICE_ID,
    "needappsflyerid": "false",
    "origin": "https://www.rappi.com.mx",
    "referer": "https://www.rappi.com.mx/",
    "user-agent": "Mozilla/5.0"
}

payload = {
    "lat": 19.4233149,
    "lng": -99.1340942,
    "store_type": "restaurant",
    "is_prime": False,
    "prime_config": {
        "unlimited_shipping": False
    }
}


def get_restaurant_data():
    response = requests.post(
        URL,
        headers=headers,
        json=payload
    )

    response.raise_for_status()
    return response.json()


def extract_products(data):

    products_list = []

    restaurant_name = data.get("name", "Unknown")

    schedule = {}

    if data.get("schedules"):
        schedule = data["schedules"][0]

    day = schedule.get("day", "")
    open_time = schedule.get("open_time", "")
    close_time = schedule.get("close_time", "")

    delivery_methods = ", ".join(
        data.get("delivery_methods", [])
    )

    for corridor in data.get("corridors", []):

        category_name = corridor.get("name", "")

        for product in corridor.get("products", []):

            original_price = product.get("price", 0)

            discount_percentage = product.get(
                "discount_percentage",
                0
            )

            discounted_price = original_price

            discounts = product.get("discounts", [])

            if discounts:
                discounted_price = discounts[0].get(
                    "price",
                    original_price
                )

            products_list.append({

                "store_id": data.get("store_id"),
                "brand_name": data.get("brand_name"),

                "restaurant": restaurant_name,
                "address": data.get("address"),

                "day": day,
                "open_time": open_time,
                "close_time": close_time,

                "delivery_methods": delivery_methods,

                "eta_value": data.get("eta"),
                "delivery_price": data.get("delivery_price"),

                "rating_score": data.get(
                    "rating",
                    {}
                ).get("score"),

                "total_reviews": data.get(
                    "rating",
                    {}
                ).get("total_reviews"),

                "category": category_name,

                "product_id": product.get(
                    "product_id"
                ),

                "product_name": product.get(
                    "name"
                ),

                "description": product.get(
                    "description",
                    ""
                ),

                "original_price": original_price,

                "discount_percentage": discount_percentage,

                "discounted_price": discounted_price
            })

    return products_list


def save_json(products):

    with open(
        "rappi_products.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            products,
            f,
            ensure_ascii=False,
            indent=4
        )


def save_csv(products):

    if not products:
        return

    with open(
        "rappi_products.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=products[0].keys()
        )

        writer.writeheader()
        writer.writerows(products)


def main():

    print("Consultando restaurante...")

    data = get_restaurant_data()

    products = extract_products(data)

    save_json(products)

    save_csv(products)

    print(
        f"Productos encontrados: {len(products)}"
    )

    print(
        f"Restaurante: {data.get('name')}"
    )

    print(
        f"ETA: {data.get('eta')}"
    )

    print(
        f"Rating: {data.get('rating', {}).get('score')}"
    )

    print(
        f"Reviews: {data.get('rating', {}).get('total_reviews')}"
    )

    print("JSON generado")
    print("CSV generado")


if __name__ == "__main__":
    main()