# 🗺️ Generador de Mapa KMZ desde Excel

Convierte un archivo Excel con coordenadas en un mapa interactivo (`.kmz`) listo para importar en **Google My Maps** o Google Earth.

---

## ✨ ¿Qué hace esta aplicación?

1. Lees tu Excel con ubicaciones (negocios, puntos de interés, clientes, etc.)
2. Subes el archivo en la web
3. Descargas un archivo `.kmz` con todos los puntos ya en el mapa
4. Importas ese archivo en Google My Maps → ¡listo!

---

## 📋 ¿Cómo debe estar tu Excel?

Tu archivo debe tener **al menos estas dos columnas**:

| Columna              | Obligatorio | Ejemplo                   |
|----------------------|-------------|---------------------------|
| `Nombre Comercial`   | ✅ Sí        | Ferretería El Tornillo     |
| `Ubicacion`          | ✅ Sí        | `19.4326, -99.1332`       |
| `Categoría`          | ❌ No        | Tienda / Restaurante / ... |
| (cualquier otra)     | ❌ No        | Aparece en el marcador    |

> 💡 **¿Cómo obtengo las coordenadas?**  
> En Google Maps, haz clic derecho sobre el lugar → aparecen las coordenadas.  
> Cópialas con este formato exacto: `latitud, longitud`

### Categorías con color automático

Si agregas una columna `Categoría`, los marcadores tendrán colores distintos:

| Categoría   | Color en mapa   |
|-------------|-----------------|
| Café / Cafetería | Naranja   |
| Restaurante      | Rojo      |
| Parque           | Verde claro |
| Tienda           | Verde amarillo |
| Farmacia         | Cian      |
| Hospital         | Blanco    |
| Banco            | Dorado    |
| Hotel            | Violeta   |
| Escuela          | Naranja   |
| Cualquier otro   | Azul      |

---

## 🚀 Cómo instalar y ejecutar

### Requisitos previos

- **Python 3.8 o superior** instalado en tu computadora
- Acceso a la terminal (CMD en Windows, Terminal en Mac/Linux)

### Paso 1: Descarga los archivos

Guarda todos los archivos en una carpeta, por ejemplo `C:\kmz-app\`

Estructura de carpetas:
```
kmz-app/
├── app.py
├── requirements.txt
└── templates/
    └── index.html
```

### Paso 2: Instala las dependencias

Abre una terminal dentro de la carpeta y escribe:

```bash
pip install -r requirements.txt
```

Espera a que termine la instalación.

### Paso 3: Ejecuta la aplicación

```bash
python app.py
```

Verás algo así:
```
 * Running on http://0.0.0.0:5000
```

### Paso 4: Abre en tu navegador

Ve a: **http://localhost:5000**

¡Ya puedes subir tu Excel y generar el mapa!

---

## 🗺️ ¿Cómo importar el KMZ en Google My Maps?

1. Ve a [maps.google.com/d](https://www.google.com/maps/d/)
2. Crea un mapa nuevo o abre uno existente
3. Haz clic en **Importar** (dentro de una capa)
4. Selecciona el archivo `mapa_generado.kmz`
5. ¡Tus puntos aparecen en el mapa!

---

## ⚠️ Solución de errores comunes

| Problema | Solución |
|----------|----------|
| "No se encontraron coordenadas" | Verifica que la columna se llame exactamente `Ubicacion` y el formato sea `lat, lon` |
| "Formato no soportado" | Usa archivos `.xlsx` o `.xls`, no `.csv` ni `.ods` |
| Marcadores en el océano | Las coordenadas pueden estar invertidas (lon, lat en vez de lat, lon) |
| El mapa no abre | El archivo se genera localmente; necesitas importarlo en Google My Maps |

---

## 🔧 Versión

- **v2.0** — Mayo 2026
- Backend: Flask + pandas + simplekml
- Frontend: HTML5 / CSS3 / JS vanilla
