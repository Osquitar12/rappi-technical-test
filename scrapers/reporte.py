import json
import re
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ==========================
# COLORES
# ==========================
RAPPI = "#FF441B"
DIDI  = "#FF6600"
UBER  = "#06C167"
GRAY  = "#F5F5F5"

# ==========================
# 1. CARGAR JSONs
# ==========================
BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, "rappi_products.json"), encoding="utf-8") as f:
    rappi_raw = json.load(f)

with open(os.path.join(BASE, "resultado_mcdonalds.json"), encoding="utf-8") as f:
    didi_raw = json.load(f)

with open(os.path.join(BASE, "ubereats_mcdonalds.json"), encoding="utf-8") as f:
    uber_raw = json.load(f)

# ==========================
# 2. NORMALIZAR
# ==========================
def parse_price(val):
    if not val:
        return None
    val = str(val).replace("MX$", "").replace("$", "").replace(",", "").strip()
    try:
        return float(val)
    except:
        return None

def parse_eta(val):
    if not val:
        return None
    m = re.search(r"(\d+)", str(val))
    return int(m.group(1)) if m else None

def parse_fee(val):
    if not val:
        return None
    if "0" in str(val) and ("gratis" in str(val).lower() or "nuevo" in str(val).lower()):
        return 0.0
    m = re.search(r"[\d.]+", str(val))
    return float(m.group()) if m else None

# --- RAPPI ---
rappi_products = []
rappi_meta = rappi_raw[0] if rappi_raw else {}
for p in rappi_raw:
    rappi_products.append({
        "platform": "Rappi",
        "name": p.get("product_name", ""),
        "description": p.get("description", ""),
        "current_price": p.get("discounted_price"),
        "original_price": p.get("original_price"),
        "discount_pct": p.get("discount_percentage", 0),
        "category": p.get("category", ""),
    })

# --- DIDI ---
didi_products = []
for p in didi_raw.get("products", []):
    didi_products.append({
        "platform": "DiDi",
        "name": p.get("name", ""),
        "description": p.get("description", ""),
        "current_price": parse_price(p.get("current_price")),
        "original_price": parse_price(p.get("original_price")),
        "discount_pct": None,
        "category": "",
    })

# --- UBER ---
uber_products = []
for p in uber_raw.get("products", []):
    uber_products.append({
        "platform": "Uber Eats",
        "name": p.get("name", ""),
        "description": p.get("description", ""),
        "current_price": parse_price(p.get("current_price")),
        "original_price": parse_price(p.get("original_price")),
        "discount_pct": None,
        "category": "",
    })

all_products = rappi_products + didi_products + uber_products

# --- MÉTRICAS por plataforma ---
platforms = {
    "Rappi": {
        "restaurant": rappi_meta.get("restaurant", "N/A"),
        "eta": parse_eta(rappi_meta.get("eta_value")),
        "delivery_fee": rappi_meta.get("delivery_price"),
        "rating": rappi_meta.get("rating_score"),
        "reviews": rappi_meta.get("total_reviews"),
        "products": rappi_products,
        "color": RAPPI,
    },
    "DiDi": {
        "restaurant": didi_raw.get("restaurant", "N/A"),
        "eta": parse_eta(didi_raw.get("eta")),
        "delivery_fee": parse_fee(didi_raw.get("delivery_fee")),
        "rating": None,
        "reviews": None,
        "products": didi_products,
        "color": DIDI,
    },
    "Uber Eats": {
        "restaurant": uber_raw.get("restaurant", "N/A"),
        "eta": parse_eta(uber_raw.get("eta")),
        "delivery_fee": parse_fee(uber_raw.get("delivery_fee")),
        "rating": None,
        "reviews": None,
        "products": uber_products,
        "color": UBER,
    },
}

# JSON consolidado
consolidated = {
    "brand": "McDonald's",
    "generated_at": __import__("datetime").datetime.now().isoformat(),
    "platforms": {
        name: {
            "restaurant": d["restaurant"],
            "eta_min": d["eta"],
            "delivery_fee_mxn": d["delivery_fee"],
            "rating": d["rating"],
            "total_reviews": d["reviews"],
            "total_products": len(d["products"]),
            "products": d["products"],
        }
        for name, d in platforms.items()
    }
}

with open(os.path.join(BASE, "consolidado.json"), "w", encoding="utf-8") as f:
    json.dump(consolidated, f, ensure_ascii=False, indent=2)
print("✅ consolidado.json guardado")

# ==========================
# 3. GRÁFICAS
# ==========================
os.makedirs("/tmp/graficas", exist_ok=True)

def savefig(name):
    path = f"/tmp/graficas/{name}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    return path

platform_names = list(platforms.keys())
p_colors = [platforms[p]["color"] for p in platform_names]

# --- G1: ETA ---
etas = [platforms[p]["eta"] or 0 for p in platform_names]
fig, ax = plt.subplots(figsize=(6, 3))
bars = ax.bar(platform_names, etas, color=p_colors, width=0.5, edgecolor="white")
for bar, val in zip(bars, etas):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f"{val} min",
            ha="center", va="bottom", fontsize=11, fontweight="bold")
ax.set_title("Tiempo de Entrega (minutos)", fontsize=13, fontweight="bold", pad=10)
ax.set_ylabel("Minutos")
ax.set_ylim(0, max(etas) * 1.3 + 5)
ax.spines[["top","right"]].set_visible(False)
ax.set_facecolor(GRAY)
savefig("g1_eta")

# --- G2: Tarifa de envío ---
fees = [platforms[p]["delivery_fee"] or 0 for p in platform_names]
fig, ax = plt.subplots(figsize=(6, 3))
bars = ax.bar(platform_names, fees, color=p_colors, width=0.5, edgecolor="white")
for bar, val in zip(bars, fees):
    label = "Gratis" if val == 0 else f"MX${val:.0f}"
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, label,
            ha="center", va="bottom", fontsize=11, fontweight="bold")
ax.set_title("Tarifa de Envío (MXN)", fontsize=13, fontweight="bold", pad=10)
ax.set_ylabel("MXN")
ax.set_ylim(0, max(fees) * 1.4 + 5)
ax.spines[["top","right"]].set_visible(False)
ax.set_facecolor(GRAY)
savefig("g2_fee")

# --- G3: Precio promedio por plataforma ---
def avg_price(prods):
    prices = [p["current_price"] for p in prods if p["current_price"] is not None]
    return round(sum(prices)/len(prices), 2) if prices else 0

avgs = [avg_price(platforms[p]["products"]) for p in platform_names]
fig, ax = plt.subplots(figsize=(6, 3))
bars = ax.bar(platform_names, avgs, color=p_colors, width=0.5, edgecolor="white")
for bar, val in zip(bars, avgs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"MX${val:.0f}",
            ha="center", va="bottom", fontsize=11, fontweight="bold")
ax.set_title("Precio Promedio de Productos (MXN)", fontsize=13, fontweight="bold", pad=10)
ax.set_ylabel("MXN")
ax.set_ylim(0, max(avgs) * 1.3 + 10)
ax.spines[["top","right"]].set_visible(False)
ax.set_facecolor(GRAY)
savefig("g3_avg_price")

# --- G4: Productos con descuento ---
def count_discounts(prods):
    return sum(1 for p in prods if (p["discount_pct"] and p["discount_pct"] > 0)
               or (p["original_price"] and p["current_price"] and p["original_price"] > p["current_price"]))

disc_counts = [count_discounts(platforms[p]["products"]) for p in platform_names]
total_counts = [len(platforms[p]["products"]) for p in platform_names]
disc_pcts = [round(d/t*100, 1) if t else 0 for d, t in zip(disc_counts, total_counts)]

fig, ax = plt.subplots(figsize=(6, 3))
x = range(len(platform_names))
bars1 = ax.bar([i - 0.2 for i in x], total_counts, width=0.35, label="Total productos", color="#CCCCCC", edgecolor="white")
bars2 = ax.bar([i + 0.2 for i in x], disc_counts, width=0.35, label="Con descuento", color=p_colors, edgecolor="white")
for bar, val in zip(bars2, disc_pcts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, f"{val}%",
            ha="center", va="bottom", fontsize=9, fontweight="bold")
ax.set_title("Productos con Descuento por Plataforma", fontsize=13, fontweight="bold", pad=10)
ax.set_xticks(list(x))
ax.set_xticklabels(platform_names)
ax.legend()
ax.spines[["top","right"]].set_visible(False)
ax.set_facecolor(GRAY)
savefig("g4_discounts")

# --- G5: Top 5 productos más baratos por plataforma ---
fig, ax = plt.subplots(figsize=(8, 4))
offset = 0
yticks, ylabels = [], []
for pname in platform_names:
    prods = [p for p in platforms[pname]["products"] if p["current_price"] is not None]
    top5 = sorted(prods, key=lambda x: x["current_price"])[:5]
    for i, prod in enumerate(top5):
        label = prod["name"][:30] + "…" if len(prod["name"]) > 30 else prod["name"]
        ax.barh(offset, prod["current_price"], color=platforms[pname]["color"], edgecolor="white", height=0.7)
        ax.text(prod["current_price"] + 1, offset, f"MX${prod['current_price']:.0f}",
                va="center", fontsize=8)
        yticks.append(offset)
        ylabels.append(f"[{pname[:1]}] {label}")
        offset += 1
    offset += 1

ax.set_yticks(yticks)
ax.set_yticklabels(ylabels, fontsize=7)
ax.set_title("Top 5 Productos más Baratos por Plataforma", fontsize=13, fontweight="bold", pad=10)
ax.set_xlabel("Precio (MXN)")
ax.spines[["top","right"]].set_visible(False)
patches = [mpatches.Patch(color=platforms[p]["color"], label=p) for p in platform_names]
ax.legend(handles=patches, loc="lower right")
plt.tight_layout()
savefig("g5_cheapest")

print("✅ Gráficas generadas")

# ==========================
# 4. PDF
# ==========================
pdf_path = os.path.join(BASE, "reporte_mcdonalds.pdf")
doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                        leftMargin=0.75*inch, rightMargin=0.75*inch,
                        topMargin=0.75*inch, bottomMargin=0.75*inch)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("title", fontSize=22, fontName="Helvetica-Bold",
                              alignment=TA_CENTER, spaceAfter=4, textColor=colors.HexColor("#1A1A2E"))
sub_style   = ParagraphStyle("sub", fontSize=11, fontName="Helvetica",
                              alignment=TA_CENTER, textColor=colors.gray, spaceAfter=16)
h1_style    = ParagraphStyle("h1", fontSize=14, fontName="Helvetica-Bold",
                              spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#1A1A2E"))
body_style  = styles["Normal"]

story = []

# Portada
story.append(Spacer(1, 0.5*inch))
story.append(Paragraph("Reporte Competitivo", title_style))
story.append(Paragraph("McDonald's — Rappi vs DiDi vs Uber Eats", sub_style))
story.append(Paragraph(f"Generado: {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}", sub_style))
story.append(Spacer(1, 0.3*inch))

# Tabla resumen de plataformas
story.append(Paragraph("Resumen por Plataforma", h1_style))
header = ["Plataforma", "Restaurante", "ETA", "Envio", "Rating", "Productos"]
rows = [header]
for pname, d in platforms.items():
    rows.append([
        pname,
        d["restaurant"][:28] + "…" if len(d["restaurant"]) > 28 else d["restaurant"],
        f"{d['eta']} min" if d["eta"] else "N/A",
        f"MX${d['delivery_fee']:.0f}" if d["delivery_fee"] is not None else "N/A",
        str(d["rating"]) if d["rating"] else "N/A",
        str(len(d["products"])),
    ])

t = Table(rows, colWidths=[1.1*inch, 2.2*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.9*inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1A1A2E")),
    ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
    ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",   (0,0), (-1,-1), 9),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor(GRAY)]),
    ("GRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
]))
story.append(t)
story.append(Spacer(1, 0.2*inch))

# Gráficas en pares
def add_image(path, w=3.2*inch):
    return Image(path, width=w, height=2.1*inch)

story.append(Paragraph("Análisis de Tiempos y Costos", h1_style))
img_row1 = Table([[add_image("/tmp/graficas/g1_eta.png"), add_image("/tmp/graficas/g2_fee.png")]],
                  colWidths=[3.4*inch, 3.4*inch])
img_row1.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"), ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
story.append(img_row1)
story.append(Spacer(1, 0.15*inch))

story.append(Paragraph("Precios y Descuentos", h1_style))
img_row2 = Table([[add_image("/tmp/graficas/g3_avg_price.png"), add_image("/tmp/graficas/g4_discounts.png")]],
                  colWidths=[3.4*inch, 3.4*inch])
img_row2.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"), ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
story.append(img_row2)

story.append(PageBreak())

story.append(Paragraph("Top 5 Productos más Baratos por Plataforma", h1_style))
story.append(add_image("/tmp/graficas/g5_cheapest.png", w=6.5*inch))
story.append(Spacer(1, 0.2*inch))

# Tabla top productos con descuento
story.append(Paragraph("Mejores Descuentos Detectados", h1_style))
disc_rows = [["Plataforma", "Producto", "Precio", "Original", "Ahorro"]]
for pname in platform_names:
    prods_with_disc = [p for p in platforms[pname]["products"]
                       if p["original_price"] and p["current_price"]
                       and p["original_price"] > p["current_price"]]
    prods_with_disc.sort(key=lambda x: (x["original_price"] - x["current_price"]), reverse=True)
    for p in prods_with_disc[:4]:
        saving = p["original_price"] - p["current_price"]
        pct = round(saving / p["original_price"] * 100)
        name = p["name"][:32] + "…" if len(p["name"]) > 32 else p["name"]
        disc_rows.append([
            pname,
            name,
            f"MX${p['current_price']:.0f}",
            f"MX${p['original_price']:.0f}",
            f"-{pct}%",
        ])

dt = Table(disc_rows, colWidths=[1.0*inch, 2.6*inch, 0.9*inch, 0.9*inch, 0.7*inch])
dt.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#FF6B35")),
    ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
    ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE",   (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor(GRAY)]),
    ("GRID", (0,0), (-1,-1), 0.4, colors.lightgrey),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))
story.append(dt)

doc.build(story)
print(f"✅ PDF guardado en reporte_mcdonalds.pdf")