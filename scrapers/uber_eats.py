"""
Scraper Uber Eats México – McDonald's más cercano
=================================================
Uso:
  python ubereats_mcdonalds.py --lat 19.4326 --lon -99.1332

Cómo obtener tus cookies:
  1. Abre https://www.ubereats.com/mx en Chrome/Firefox
  2. Inicia sesión (o entra como invitado)
  3. Abre DevTools → Application → Cookies → www.ubereats.com
  4. Copia los valores de  "sid"  y  "csid"  y pégalos abajo
"""

import argparse, json, math, time, sys
import requests

# ══════════════════════════════════════════════════════════════
#  ▶  PON AQUÍ TUS COOKIES (se obtienen del navegador)
# ══════════════════════════════════════════════════════════════
MY_COOKIES = {
    # Ejemplo:
   "sid":"g.a000-gi-FBXgaG_ZK1Gwl3fB4CI-eNXWBryaRe_PkMfWRAAp-SOJErmh,FzZ4cYc41snzcPC0JAACgYKAdESARQSFQHGX2MiWxeeS3kgxq1ncD1CvqTGvhoVAUF8yKpTln41rFhmhrqXeq13Iys70076",
    "csid":"1781524275975::fOLYfZu8WbmvgjGIRm8C.6.1781524283528.0::1.2336.0::0.0.0.0::0.0.0"# "csid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
}
# ══════════════════════════════════════════════════════════════


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":           "application/json, text/plain, */*",
    "Accept-Language":  "es-MX,es;q=0.9,en;q=0.8",
    "Content-Type":     "application/json",
    "Origin":           "https://www.ubereats.com",
    "Referer":          "https://www.ubereats.com/mx",
    "x-csrf-token":     "x",
}

BASE = "https://www.ubereats.com/api"


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlon/2)**2)
    return R * 2 * math.asin(math.sqrt(a))


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)
    if MY_COOKIES:
        s.cookies.update(MY_COOKIES)
    return s


# ─────────────────────────────────────────────
#  1. BUSCAR McDONALD'S
# ─────────────────────────────────────────────

def search_mcdonalds(lat: float, lon: float, s: requests.Session) -> list[dict]:
    url     = f"{BASE}/getFeedV1"
    payload = {
        "cacheKey":   "",
        "feedVersion": "2",
        "feedType":   "SEARCH",
        "userQuery":  "McDonald's",
        "locationType": "GEOGRAPHIC",
        "longitude":  lon,
        "latitude":   lat,
        "pageInfo":   {"offset": 0, "pageSize": 30},
        "marketingFeedType": "NONE",
        "billboardUuid": "",
        "targetLocation": {
            "latitude":  lat,
            "longitude": lon,
            "reference":   "geo",
            "referenceId": f"{lat},{lon}",
            "type":        "geocode",
        },
    }

    print(f"\n🔍  Buscando McDonald's cerca de ({lat}, {lon}) …")
    resp = s.post(url, json=payload, timeout=20)

    if resp.status_code == 403:
        print("\n⚠️   Uber Eats devolvió 403 – necesitas pegar tus cookies en MY_COOKIES.")
        print("     Revisa las instrucciones al inicio del script.\n")
        sys.exit(1)

    resp.raise_for_status()
    data = resp.json()

    stores = []
    feed_items = (
        data.get("data", {})
            .get("feedItems", [])
    )

    for item in feed_items:
        store = item.get("store", {})
        if not store:
            continue
        title = (store.get("title") or {}).get("text", "")
        if "mcdonald" not in title.lower():
            continue
        loc = store.get("location") or {}
        stores.append({
            "uuid":    store.get("storeUuid"),
            "name":    title,
            "lat":     loc.get("latitude"),
            "lon":     loc.get("longitude"),
            "address": (loc.get("address") or {}).get("address1", ""),
            "rating":  store.get("rating", {}).get("ratingValue"),
        })

    return stores


# ─────────────────────────────────────────────
#  2. EL MÁS CERCANO
# ─────────────────────────────────────────────

def closest(stores: list[dict], lat: float, lon: float) -> dict:
    def dist(st):
        if st["lat"] is None or st["lon"] is None:
            return float("inf")
        return haversine(lat, lon, st["lat"], st["lon"])
    return min(stores, key=dist)


# ─────────────────────────────────────────────
#  3. MENÚ Y PRECIOS
# ─────────────────────────────────────────────

def get_menu(uuid: str, s: requests.Session) -> list[dict]:
    url     = f"{BASE}/getStoreV1"
    payload = {"storeUuid": uuid}

    print(f"\n📋  Descargando menú …")
    resp = s.post(url, json=payload, timeout=25)
    resp.raise_for_status()
    data = resp.json()

    items = []
    catalog_map = (
        data.get("data", {})
            .get("catalogSectionsMap", {})
    )

    for section_list in catalog_map.values():
        for section in section_list:
            cat = (section.get("title") or {}).get("text", "Sin categoría")
            for raw in section.get("itemV2", []):
                info  = raw.get("catalogItem", {})
                title = info.get("title", "")
                desc  = info.get("itemDescription", "")
                price = info.get("price")           # centavos MXN
                imgs  = info.get("imageUrls") or []
                items.append({
                    "category":    cat,
                    "name":        title,
                    "description": desc,
                    "price_mxn":   round(price / 100, 2) if price else None,
                    "image_url":   imgs[0] if imgs else "",
                })

    return items


# ─────────────────────────────────────────────
#  4. SALIDA EN CONSOLA
# ─────────────────────────────────────────────

def print_results(store: dict, menu: list[dict], user_lat: float, user_lon: float):
    dist = haversine(user_lat, user_lon, store["lat"], store["lon"])
    print("\n" + "═"*62)
    print(f"  🍔  {store['name']}")
    print(f"  📍  {store['address']}")
    print(f"  🌐  Latitud  : {store['lat']}")
    print(f"  🌐  Longitud : {store['lon']}")
    print(f"  📏  Distancia: {dist:.2f} km")
    if store.get("rating"):
        print(f"  ⭐  Rating   : {store['rating']}")
    print("═"*62)

    if not menu:
        print("  ⚠️   No se obtuvieron items del menú.")
        return

    cat_actual = None
    for it in menu:
        if it["category"] != cat_actual:
            cat_actual = it["category"]
            print(f"\n  ▸ {cat_actual}")
        precio = (f"${it['price_mxn']:.2f} MXN"
                  if it["price_mxn"] is not None else "—")
        print(f"    • {it['name']:<42} {precio}")

    print("\n" + "═"*62)
    print(f"  Total de items: {len(menu)}")


# ─────────────────────────────────────────────
#  5. GUARDAR JSON
# ─────────────────────────────────────────────

def save_json(store: dict, menu: list[dict], user_lat: float, user_lon: float, path: str):
    dist = haversine(user_lat, user_lon, store["lat"], store["lon"])
    out = {
        "consulta": {
            "latitud_usuario":   user_lat,
            "longitud_usuario":  user_lon,
        },
        "restaurante": {
            "nombre":    store["name"],
            "direccion": store["address"],
            "latitud":   store["lat"],
            "longitud":  store["lon"],
            "distancia_km": round(dist, 3),
            "rating":    store.get("rating"),
            "uuid":      store["uuid"],
        },
        "menu": menu,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n  💾  Resultado guardado en: {path}")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="Scraper Uber Eats MX – McDonald's más cercano"
    )
    p.add_argument("--lat", type=float, default=19.4326,
                   help="Latitud  (default: Zócalo CDMX)")
    p.add_argument("--lon", type=float, default=-99.1332,
                   help="Longitud (default: Zócalo CDMX)")
    p.add_argument("--out", default="resultado.json",
                   help="Archivo de salida (default: resultado.json)")
    args = p.parse_args()

    s = make_session()

    # 1. Buscar
    stores = search_mcdonalds(args.lat, args.lon, s)
    if not stores:
        print("❌  No se encontraron McDonald's. Intenta con otras coordenadas.")
        return

    print(f"✅  {len(stores)} sucursal(es) encontrada(s).")

    # 2. Más cercana
    store = closest(stores, args.lat, args.lon)

    # 3. Menú
    time.sleep(0.6)
    menu = get_menu(store["uuid"], s)

    # 4. Mostrar
    print_results(store, menu, args.lat, args.lon)

    # 5. Guardar
    save_json(store, menu, args.lat, args.lon, args.out)


if __name__ == "__main__":
    main()