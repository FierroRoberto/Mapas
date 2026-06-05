# 🗺️ Excel a Google My Maps (KMZ)

Aplicación web que convierte un archivo Excel con direcciones o coordenadas en un mapa interactivo (formato KMZ) compatible con **Google My Maps** y **Google Earth**.

## ✨ Características

- Sube un archivo Excel (`.xlsx` o `.xls`) con tus ubicaciones.
- Detecta automáticamente las columnas:
  - **Nombre Comercial** (obligatorio)
  - **Latitud** y **Longitud** (opcional, si ya tienes coordenadas)
  - **Dirección** (opcional, geocodificación automática con Google Maps API)
  - **Categoría** (opcional, asigna colores a los marcadores)
- Muestra toda la información de cada fila en la ventana emergente del marcador.
- Genera un archivo `.kmz` listo para importar en Google My Maps.
- Interfaz web sencilla con arrastrar y soltar archivos.

## 📋 Requisitos previos

- Python 3.8 o superior
- pip (administrador de paquetes de Python)
- (Opcional) Clave de API de Google Maps Geocoding si usas direcciones en lugar de coordenadas.

## 🚀 Instalación y ejecución local

1. **Clona el repositorio** (o descarga los archivos):
   ```bash
   git clone https://github.com/tu-usuario/excel-a-google-maps.git
   cd excel-a-google-maps