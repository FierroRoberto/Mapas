# 🗺️ Generador de Mapa KMZ desde Excel

Convierte un archivo Excel con coordenadas en un mapa interactivo (`.kmz`) listo para importar en **Google My Maps** o Google Earth.

> ✅ **100% en el navegador** — Ningún dato se envía a ningún servidor. Todo el procesamiento ocurre localmente en tu computadora.

---

## 🌐 Ver la app en línea

👉 **https://TU-USUARIO.github.io/TU-REPOSITORIO**

*(Reemplaza con tu usuario y nombre de repositorio de GitHub)*

---

## 📋 ¿Cómo debe estar tu Excel?

Tu archivo debe tener **al menos estas dos columnas**:

| Columna            | Obligatorio | Ejemplo                |
|--------------------|-------------|------------------------|
| `Nombre Comercial` | ✅ Sí        | Ferretería El Tornillo |
| `Ubicacion`        | ✅ Sí        | `19.4326, -99.1332`   |
| `Categoría`        | ❌ No        | Tienda / Restaurante   |
| (cualquier otra)   | ❌ No        | Aparece en el marcador |

> 💡 **¿Cómo obtengo las coordenadas?**
> En Google Maps, haz clic derecho sobre el lugar → aparecen las coordenadas.
> Cópialas con este formato: `latitud, longitud`

### Categorías con color automático

| Categoría        | Color       |
|------------------|-------------|
| Café / Cafetería | Naranja     |
| Restaurante      | Rojo        |
| Parque           | Verde claro |
| Tienda           | Amarillo    |
| Farmacia         | Cian        |
| Hospital         | Blanco      |
| Banco            | Dorado      |
| Hotel            | Violeta     |
| Escuela          | Naranja     |
| Cualquier otro   | Azul        |

---

## 🚀 Cómo subir a GitHub y activar GitHub Pages

### Paso 1 — Crear el repositorio en GitHub

1. Ve a [github.com](https://github.com) e inicia sesión
2. Clic en **"New repository"** (botón verde, arriba a la derecha)
3. Ponle un nombre, por ejemplo: `mapa-kmz`
4. Déjalo en **Public**
5. Clic en **"Create repository"**

---

### Paso 2 — Subir los archivos

#### Opción A: Desde el navegador (más fácil, sin instalar nada)

1. En tu repositorio recién creado, clic en **"uploading an existing file"**
2. Arrastra el archivo `index.html` a la ventana
3. Clic en **"Commit changes"** (botón verde abajo)

#### Opción B: Desde la terminal (Git)

```bash
# Clona tu repositorio vacío
git clone https://github.com/TU-USUARIO/mapa-kmz.git
cd mapa-kmz

# Copia el archivo index.html aquí y luego:
git add index.html
git commit -m "Agregar generador de mapas KMZ"
git push origin main
```

---

### Paso 3 — Activar GitHub Pages

1. En tu repositorio, clic en **"Settings"** (pestaña con ícono de engrane)
2. En el menú izquierdo, clic en **"Pages"**
3. En la sección **"Branch"**, selecciona `main` y carpeta `/ (root)`
4. Clic en **"Save"**
5. Espera 1-2 minutos y aparecerá tu URL:
   ```
   https://TU-USUARIO.github.io/mapa-kmz
   ```

---

### Paso 4 — ¡Listo!

Comparte esa URL con quien quieras. Funciona en cualquier navegador, en computadora y en celular.

---

## 🗺️ ¿Cómo importar el KMZ en Google My Maps?

1. Ve a [maps.google.com/d](https://www.google.com/maps/d/)
2. Crea un mapa nuevo o abre uno existente
3. Clic en **"Importar"** (dentro de una capa)
4. Selecciona el archivo `mapa_generado.kmz`
5. ¡Tus puntos aparecen en el mapa!

---

## ⚠️ Solución de errores comunes

| Problema | Solución |
|----------|----------|
| "Sin coordenadas válidas" | La columna debe llamarse exactamente `Ubicacion` (sin tilde) y el formato ser `lat, lon` |
| "Formato no válido" | Usa `.xlsx` o `.xls`, no `.csv` ni `.ods` |
| Marcadores en el océano | Las coordenadas pueden estar invertidas (lon, lat) — la app intenta corregirlo automáticamente |
| La página da error 404 | Espera 2 minutos después de activar GitHub Pages y recarga |

---

## 🛠️ Tecnologías utilizadas

- **[SheetJS](https://sheetjs.com/)** — Lee archivos Excel directamente en el navegador
- **[JSZip](https://stuk.github.io/jszip/)** — Genera el archivo KMZ (que es un ZIP con un KML adentro)
- HTML5 / CSS3 / JavaScript puro — Sin frameworks, sin servidor

---

## 📁 Estructura del proyecto

```
mapa-kmz/
└── index.html     ← toda la app en un solo archivo
```

---

*Versión 2.0 — Junio 2026*
