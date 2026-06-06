"""
app.py — Generador de KMZ desde Excel
Versión mejorada: manejo robusto de errores, validaciones claras,
retroalimentación detallada al usuario.
"""

import os
import re
import tempfile
import logging

import pandas as pd
import simplekml
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename

# ─────────────────────────────────────────────
# Configuración de la aplicación
# ─────────────────────────────────────────────
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB máximo
app.config["UPLOAD_FOLDER"] = tempfile.gettempdir()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Paleta de colores por categoría
# (KML usa AABBGGRR — alpha, blue, green, red)
# ─────────────────────────────────────────────
CATEGORY_COLORS = {
    "café":         simplekml.Color.orangered,
    "cafeteria":    simplekml.Color.orangered,
    "restaurante":  simplekml.Color.red,
    "parque":       simplekml.Color.lightgreen,
    "tienda":       simplekml.Color.yellowgreen,
    "farmacia":     simplekml.Color.cyan,
    "hospital":     simplekml.Color.white,
    "banco":        simplekml.Color.gold,
    "hotel":        simplekml.Color.violet,
    "escuela":      simplekml.Color.orange,
    "oficina":      simplekml.Color.cornflowerblue,
    "default":      simplekml.Color.dodgerblue,
}

# Íconos personalizados de Google Maps por categoría
CATEGORY_ICONS = {
    "café":         "http://maps.google.com/mapfiles/ms/icons/orange-dot.png",
    "cafeteria":    "http://maps.google.com/mapfiles/ms/icons/orange-dot.png",
    "restaurante":  "http://maps.google.com/mapfiles/ms/icons/red-dot.png",
    "parque":       "http://maps.google.com/mapfiles/ms/icons/green-dot.png",
    "tienda":       "http://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
    "farmacia":     "http://maps.google.com/mapfiles/ms/icons/ltblue-dot.png",
    "hospital":     "http://maps.google.com/mapfiles/ms/icons/pink-dot.png",
    "banco":        "http://maps.google.com/mapfiles/ms/icons/purple-dot.png",
    "hotel":        "http://maps.google.com/mapfiles/ms/icons/purple-dot.png",
    "escuela":      "http://maps.google.com/mapfiles/ms/icons/orange-dot.png",
    "default":      "http://maps.google.com/mapfiles/ms/icons/blue-dot.png",
}


# ─────────────────────────────────────────────
# Utilidades
# ─────────────────────────────────────────────

def parse_ubicacion(value) -> tuple[float | None, float | None]:
    """
    Extrae (latitud, longitud) de una celda con formato 'lat, lon'.
    Acepta: '19.4326, -99.1332'  |  '19.4326 -99.1332'  |  '19.4326,-99.1332'
    Devuelve (None, None) si no se puede parsear.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None, None

    texto = str(value).strip()
    partes = re.split(r"[,\s]+", texto)
    numeros: list[float] = []

    for p in partes:
        p = p.strip()
        if not p:
            continue
        try:
            numeros.append(float(p))
        except ValueError:
            continue
        if len(numeros) == 2:
            break

    if len(numeros) == 2:
        lat, lon = numeros
        # Validación básica de rango geográfico
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return lat, lon
        # Quizás venían invertidas
        if -90 <= lon <= 90 and -180 <= lat <= 180:
            return lon, lat

    return None, None


def find_column(columns: list[str], candidates: list[str]) -> str | None:
    """Busca la primera columna que coincida (sin importar mayúsculas/tildes)."""
    lower_cols = {c.lower().strip(): c for c in columns}
    for candidate in candidates:
        if candidate.lower() in lower_cols:
            return lower_cols[candidate.lower()]
    return None


def get_icon(categoria: str) -> tuple[str, int]:
    """Devuelve (url_ícono, color_kml) según la categoría."""
    cat_lower = str(categoria).lower() if categoria else ""
    for key in CATEGORY_ICONS:
        if key in cat_lower:
            return CATEGORY_ICONS[key], CATEGORY_COLORS[key]
    return CATEGORY_ICONS["default"], CATEGORY_COLORS["default"]


# ─────────────────────────────────────────────
# Lógica principal
# ─────────────────────────────────────────────

def generate_kmz_from_excel(filepath: str) -> dict:
    """
    Lee el Excel y genera un archivo KMZ temporal.

    Retorna un diccionario con:
        kmz_path   – ruta al .kmz generado
        total      – filas leídas
        ok         – marcadores colocados
        errores    – lista de mensajes de error por fila
        warnings   – advertencias no fatales
    """
    # ── Leer Excel ──────────────────────────────────────────────────────────
    try:
        df = pd.read_excel(filepath, dtype=str)
    except Exception as exc:
        raise ValueError(f"No se pudo leer el archivo Excel: {exc}") from exc

    if df.empty:
        raise ValueError("El archivo Excel está vacío. Agrega datos e intenta de nuevo.")

    df.columns = [str(c).strip() for c in df.columns]
    cols = df.columns.tolist()
    total = len(df)

    # ── Detectar columnas ────────────────────────────────────────────────────
    nombre_col = find_column(cols, ["Nombre Comercial", "Nombre", "Negocio", "Establecimiento", "Name"])
    if not nombre_col:
        nombre_col = cols[0]  # fallback: primera columna

    ubicacion_col = find_column(cols, ["Ubicacion", "Ubicación", "Coordenadas", "Coords"])
    lat_col       = find_column(cols, ["Latitud", "Latitude", "Lat"])
    lon_col       = find_column(cols, ["Longitud", "Longitude", "Lon", "Lng"])
    cat_col       = find_column(cols, ["Categoría", "Categoria", "Tipo", "Category"])

    # ── Construir KML ────────────────────────────────────────────────────────
    kml = simplekml.Kml(name="Mapa GAFI")
    errores: list[str] = []
    warnings: list[str] = []
    marcadores_ok = 0

    for idx, row in df.iterrows():
        fila_num = idx + 2  # +2 porque idx=0 es fila 2 en Excel (fila 1 = encabezados)
        nombre = str(row[nombre_col]).strip() if pd.notna(row[nombre_col]) else f"Punto {fila_num}"
        lat, lon = None, None

        # Prioridad 1: columna Ubicacion
        if ubicacion_col and pd.notna(row.get(ubicacion_col, None)):
            lat, lon = parse_ubicacion(row[ubicacion_col])

        # Prioridad 2: columnas Latitud / Longitud separadas
        if lat is None and lat_col and lon_col:
            try:
                lat_raw = row.get(lat_col)
                lon_raw = row.get(lon_col)
                if pd.notna(lat_raw) and pd.notna(lon_raw):
                    lat = float(lat_raw)
                    lon = float(lon_raw)
                    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                        errores.append(
                            f"Fila {fila_num} — '{nombre}': "
                            f"coordenadas fuera de rango (lat={lat}, lon={lon}). "
                            "Verifica que Latitud esté entre -90 y 90, y Longitud entre -180 y 180."
                        )
                        lat = lon = None
            except (ValueError, TypeError):
                lat = lon = None

        if lat is None or lon is None:
            msg = (
                f"Fila {fila_num} — '{nombre}': "
                "no se encontraron coordenadas válidas. "
                "Asegúrate de tener una columna 'Ubicacion' con formato 'latitud, longitud'."
            )
            errores.append(msg)
            continue

        # ── Crear punto en el mapa ───────────────────────────────────────────
        point = kml.newpoint(name=nombre[:200], coords=[(lon, lat)])

        # Descripción HTML enriquecida
        html_rows = ""
        for col in cols:
            if col in {nombre_col, ubicacion_col, lat_col, lon_col}:
                continue
            val = row.get(col, "")
            if pd.notna(val) and str(val).strip():
                html_rows += (
                    f"<tr>"
                    f"<td style='padding:4px 8px;font-weight:bold;color:#555;white-space:nowrap'>{col}</td>"
                    f"<td style='padding:4px 8px;color:#222'>{val}</td>"
                    f"</tr>"
                )

        point.description = (
            f"<div style='font-family:Segoe UI,Arial,sans-serif;min-width:200px'>"
            f"<h3 style='margin:0 0 8px;color:#1a73e8'>{nombre}</h3>"
            f"<table style='border-collapse:collapse;width:100%'>{html_rows}</table>"
            f"<p style='margin:8px 0 0;font-size:11px;color:#aaa'>Lat: {lat:.6f} | Lon: {lon:.6f}</p>"
            f"</div>"
        )

        # Estilo del ícono
        categoria = str(row.get(cat_col, "")) if cat_col and pd.notna(row.get(cat_col, None)) else ""
        icon_url, color = get_icon(categoria)

        point.style.iconstyle.icon.href = icon_url
        point.style.iconstyle.color = color
        point.style.iconstyle.scale = 1.3
        point.style.labelstyle.scale = 0.85

        marcadores_ok += 1

    if marcadores_ok == 0:
        raise ValueError(
            "No se pudo crear ningún marcador. "
            "Revisa que tu Excel tenga una columna 'Ubicacion' con coordenadas válidas "
            "(ejemplo: 19.4326, -99.1332)."
        )

    # ── Guardar KMZ ─────────────────────────────────────────────────────────
    tmp = tempfile.NamedTemporaryFile(suffix=".kmz", delete=False)
    kml.savekmz(tmp.name)
    tmp.close()

    return {
        "kmz_path":  tmp.name,
        "total":     total,
        "ok":        marcadores_ok,
        "errores":   errores,
        "warnings":  warnings,
    }


# ─────────────────────────────────────────────
# Rutas Flask
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    # Validar que venga un archivo
    if "excel_file" not in request.files:
        return jsonify({"error": "No se envió ningún archivo."}), 400

    file = request.files["excel_file"]

    if not file.filename:
        return jsonify({"error": "El nombre del archivo está vacío."}), 400

    if not file.filename.lower().endswith((".xlsx", ".xls")):
        return jsonify({"error": "Formato no soportado. Usa un archivo .xlsx o .xls de Excel."}), 400

    filename  = secure_filename(file.filename)
    temp_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(temp_path)

    try:
        result = generate_kmz_from_excel(temp_path)
    except ValueError as exc:
        # Error controlado — mensaje amigable
        _cleanup(temp_path)
        return jsonify({"error": str(exc)}), 422
    except Exception as exc:
        logger.exception("Error inesperado procesando %s", filename)
        _cleanup(temp_path)
        return jsonify({"error": f"Error interno al procesar el archivo: {exc}"}), 500
    finally:
        _cleanup(temp_path)

    # Devolver el archivo KMZ con cabeceras de resumen
    response = send_file(
        result["kmz_path"],
        as_attachment=True,
        download_name="mapa_generado.kmz",
        mimetype="application/vnd.google-earth.kmz",
    )
    # Cabeceras personalizadas para que el frontend muestre el resumen
    response.headers["X-Markers-Ok"]    = result["ok"]
    response.headers["X-Markers-Total"] = result["total"]
    response.headers["X-Errors-Count"]  = len(result["errores"])
    response.headers["X-Errors-Detail"] = " | ".join(result["errores"][:10])  # máx 10
    response.headers["Access-Control-Expose-Headers"] = (
        "X-Markers-Ok, X-Markers-Total, X-Errors-Count, X-Errors-Detail"
    )
    return response


def _cleanup(path: str):
    """Elimina el archivo temporal si existe."""
    try:
        if path and os.path.exists(path):
            os.unlink(path)
    except OSError:
        pass


# ─────────────────────────────────────────────
# Punto de entrada
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
