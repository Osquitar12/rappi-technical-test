# 🍔 Competitive Intelligence

Sistema de **inteligencia competitiva** desarrollado para recolectar, analizar y comparar información de productos de McDonald's en diferentes plataformas de delivery:

- 🟠 Rappi
- 🔵 DiDi Food
- 🟢 Uber Eats

El sistema automatiza la extracción de productos, precios, descuentos, tiempos de entrega y costos de envío. Posteriormente consolida la información y genera un reporte competitivo con métricas y gráficas comparativas.

---

## 📌 Objetivo del proyecto

Construir un sistema automático de recolección de datos que permita analizar la presencia de McDonald's en diferentes plataformas digitales, identificando:

- Diferencias de precios.
- Productos disponibles.
- Promociones y descuentos.
- Costos de envío.
- Tiempos estimados de entrega.
- Comparación competitiva entre plataformas.

---

## 📁 Estructura del proyecto

```
competitive-intelligence/
│
├── main.py                  # Ejecuta todo el flujo del proyecto
│
├── save_didi_session.py     # Guarda sesión inicial de DiDi Food
├── clear_didi_storage.py    # Limpia información almacenada de DiDi
│
├── didi.py                  # Scraper de DiDi Food
├── rappi.py                 # Scraper de Rappi
├── uber_eats.py             # Scraper de Uber Eats
│
├── reporte.py                # Generación del reporte competitivo
│
├── requirements.txt         # Librerías necesarias
│
├── didi_profile/            # Sesión local del navegador DiDi
│
├── resultados/
│   ├── JSON generados
│   ├── Archivos Excel
│   └── Reporte PDF
│
└── README.md
```

---

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Osquitar12/rappi-technical-test.git
```

Ingresar al proyecto:

```bash
cd competitive-intelligence
```

### 2. Crear entorno virtual

Crear entorno:

```bash
python -m venv .venv
```

Activar entorno virtual:

**Windows**
```bash
.venv\Scripts\activate
```

**Mac / Linux**
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

Ejecutar:

```bash
pip install -r requirements.txt
```

Instalar navegador requerido por Playwright:

```bash
playwright install chromium
```

---

## 🔐 Configuración inicial de DiDi Food

Antes de ejecutar el proyecto completo es necesario crear una sesión válida de DiDi Food.

Este paso se realiza solamente la primera vez.

Ejecutar:

```bash
python save_didi_session.py
```

**Proceso:**

1. Se abrirá automáticamente un navegador.
2. Iniciar sesión manualmente en DiDi Food.
3. Esperar a que la sesión quede guardada.
4. Cerrar el navegador.

Después de completar este proceso se generará la carpeta:

```
didi_profile/
```

Esta carpeta contiene la sesión utilizada por el scraper de DiDi Food.

Si la sesión expira o se elimina, repetir nuevamente este paso.

---

## 🚀 Ejecución del proyecto

### Paso 1: Crear sesión DiDi

Ejecutar primero:

```bash
python save_didi_session.py
```

### Paso 2: Ejecutar el flujo completo

Después de tener la sesión creada:

```bash
python main.py
```

El archivo `main.py` ejecuta automáticamente:

```
1. Scraper DiDi Food
        ↓
2. Scraper Rappi
        ↓
3. Scraper Uber Eats
        ↓
4. Consolidación de información
        ↓
5. Generación del reporte PDF
```

---

## 🕷️ Funcionamiento de los Scrapers

### DiDi Food

Obtiene:

- Productos disponibles.
- Precios.
- Descuentos.
- Información del restaurante.
- Tiempo estimado de entrega.
- Costo de envío.

Utiliza una sesión persistente del navegador para mantener autenticación.

### Rappi

Obtiene:

- Catálogo de productos.
- Precios actuales.
- Información del restaurante.
- Datos disponibles públicamente.

### Uber Eats

Obtiene:

- Menú completo.
- Productos.
- Descripciones.
- Precios.
- Promociones.
- Información de entrega.

---

## 📄 Archivos generados

Después de ejecutar el proyecto se generan los siguientes archivos:

| Archivo | Descripción |
|---|---|
| `resultado_mcdonalds.json` | Datos obtenidos desde DiDi Food |
| `resultado_mcdonalds.xlsx` | Datos DiDi Food en formato Excel |
| `rappi_products.json` | Datos obtenidos desde Rappi |
| `rappi_products.csv` | Datos Rappi en formato CSV |
| `ubereats_mcdonalds.json` | Datos obtenidos desde Uber Eats |
| `ubereats_mcdonalds.xlsx` | Datos Uber Eats en Excel |
| `consolidado.json` | Información consolidada de todas las plataformas |
| `reporte_mcdonalds.pdf` | Reporte final de inteligencia competitiva |

---

## 📊 Reporte competitivo generado

El reporte PDF incluye:

### Comparación general

- Plataforma.
- Restaurante.
- Cantidad de productos.
- Tiempo estimado de entrega.
- Costo de envío.

### Análisis de precios

- Precio promedio por plataforma.
- Productos más económicos.
- Diferencias de precios.

### Análisis de promociones

- Cantidad de productos con descuento.
- Mejores descuentos encontrados.

### Visualizaciones

Incluye gráficas comparativas de:

- Tiempo de entrega.
- Costos de envío.
- Precio promedio.
- Productos con descuento.
- Comparaciones entre plataformas.

---

## 🧹 Solución de problemas

### DiDi conserva una dirección antigua

Ejecutar:

```bash
python clear_didi_storage.py
```

Después crear nuevamente la sesión:

```bash
python save_didi_session.py
```

### Error con Playwright

Instalar nuevamente Chromium:

```bash
playwright install chromium
```

### Error de dependencias

Actualizar paquetes:

```bash
pip install -r requirements.txt --upgrade
```

---

## ✅ Flujo correcto de ejecución

Siempre seguir este orden:

1. Crear entorno virtual.
2. Instalar dependencias.
3. Ejecutar `python save_didi_session.py`.
4. Ejecutar `python main.py`.
5. Revisar archivos generados.

---

## 👨‍💻 Tecnologías utilizadas

- Python
- Playwright
- Requests
- BeautifulSoup
- Pandas
- OpenPyXL
- Matplotlib
- ReportLab

---

## 📌 Notas finales

- La sesión de DiDi Food debe ser creada antes de ejecutar el scraper completo.
- El proyecto está diseñado para ejecutarse mediante un único punto de entrada (`main.py`).
- Los resultados generados permiten realizar análisis competitivo entre plataformas de delivery.

---

Este README está orientado a una **prueba técnica**, ya que documenta instalación, ejecución y arquitectura del proyecto.
