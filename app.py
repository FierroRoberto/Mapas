import os
import tempfile
import pandas as pd
import simplekml
import requests
import time
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB límite
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Configuración (opcional: tu API Key de Google para geocodificación)
GOOGLE_API_KEY = ""  # Déjalo vacío si no usas geocodificación
GEOCODING_ENABLED = True  # Si no tienes API, ponlo en False

def geocode_address(address, api_key):
    """Geocodifica una dirección usando Google Maps Geocoding API."""
    if not api_key or not address:
        return None, None
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("status") == "OK" and data["results"]:
            loc = data["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
    except Exception as e:
        print(f"Error geocodificando: {e}")
    return None, None

def generate_kmz_from_excel(filepath):
    """Procesa el archivo Excel y genera un KMZ en memoria."""
    df = pd.read_excel(filepath, dtype=str)
    kml = simplekml.Kml(name="Mapa desde Excel")
    
    # Normalizar nombres de columnas
    df.columns = [str(col).strip() for col in df.columns]
    cols = df.columns.tolist()
    
    # Identificar columna de nombre comercial
    nombre_col = None
    for candidate in ["Nombre Comercial", "nombre", "Negocio", "Establecimiento"]:
        if candidate in cols:
            nombre_col = candidate
            break
    if not nombre_col:
        nombre_col = cols[0]  # fallback: primera columna
    
    # Identificar coordenadas o dirección
    lat_col = next((c for c in cols if c.lower() in ["latitud", "latitude", "lat"]), None)
    lon_col = next((c for c in cols if c.lower() in ["longitud", "longitude", "lon", "lng"]), None)
    dir_col = next((c for c in cols if c.lower() in ["dirección", "direccion", "address"]), None)
    
    # Columna de categoría para colores (opcional)
    cat_col = next((c for c in cols if c.lower() in ["categoría", "categoria", "tipo"]), None)
    
    marcadores_ok = 0
    errores = []
    
    for idx, row in df.iterrows():
        nombre = row[nombre_col] if pd.notna(row[nombre_col]) else f"Punto {idx+1}"
        lat, lon = None, None
        
        # 1. Intentar con coordenadas explícitas
        if lat_col and lon_col:
            try:
                lat = float(row[lat_col]) if pd.notna(row[lat_col]) else None
                lon = float(row[lon_col]) if pd.notna(row[lon_col]) else None
            except (ValueError, TypeError):
                lat = lon = None
        
        # 2. Si no hay coordenadas y hay dirección, geocodificar
        if (lat is None or lon is None) and dir_col and GEOCODING_ENABLED:
            direccion = row[dir_col] if pd.notna(row[dir_col]) else None
            if direccion:
                lat, lon = geocode_address(direccion, GOOGLE_API_KEY)
                time.sleep(0.1)  # respetar cuotas
        
        if lat is None or lon is None:
            errores.append(f"Fila {idx+1}: '{nombre}' - sin coordenadas válidas")
            continue
        
        # Crear punto
        point = kml.newpoint(name=str(nombre)[:200], coords=[(lon, lat)])
        
        # Descripción HTML con todas las columnas
        html_desc = f"<div style='font-family:Arial'><b>{nombre}</b><br/><hr/>"
        for col in cols:
            if col != nombre_col and pd.notna(row[col]) and str(row[col]).strip():
                html_desc += f"<b>{col}:</b> {row[col]}<br/>"
        html_desc += "</div>"
        point.description = html_desc
        
        # Estilo: color según categoría si existe
        if cat_col and pd.notna(row[cat_col]):
            categoria = str(row[cat_col]).lower()
            if "café" in categoria or "cafeteria" in categoria:
                color = simplekml.Color.orangered
            elif "restaurante" in categoria:
                color = simplekml.Color.red
            elif "parque" in categoria:
                color = simplekml.Color.lightgreen
            elif "tienda" in categoria:
                color = simplekml.Color.yellowgreen
            else:
                color = simplekml.Color.green
        else:
            color = simplekml.Color.green
        
        point.style.iconstyle.color = color
        point.style.iconstyle.scale = 1.2
        marcadores_ok += 1
    
    # Guardar en archivo temporal
    temp_kmz = tempfile.NamedTemporaryFile(suffix=".kmz", delete=False)
    kml.savekmz(temp_kmz.name)
    temp_kmz.close()
    
    return temp_kmz.name, marcadores_ok, errores

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'excel_file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400
    
    file = request.files['excel_file']
    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({"error": "Formato no soportado. Use .xlsx o .xls"}), 400
    
    # Guardar archivo temporalmente
    filename = secure_filename(file.filename)
    temp_input = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(temp_input)
    
    try:
        kmz_path, count, errors = generate_kmz_from_excel(temp_input)
        os.unlink(temp_input)  # eliminar Excel temporal
        
        # Enviar el archivo KMZ
        return send_file(
            kmz_path,
            as_attachment=True,
            download_name="mapa_generado.kmz",
            mimetype='application/vnd.google-earth.kmz'
        )
    except Exception as e:
        # Limpiar y devolver error
        if os.path.exists(temp_input):
            os.unlink(temp_input)
        return jsonify({"error": f"Error procesando el archivo: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)