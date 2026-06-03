# Generador de mapas desde Excel a Google My Maps

Convierte un archivo Excel con direcciones o coordenadas en un mapa interactivo para Google My Maps, usando Google Colab (sin instalar nada).

## Cómo usar
1. Abre el cuaderno de Colab: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/TU_USUARIO/TU_REPOSITORIO/blob/main/colab_notebook.ipynb)
   (cambia la URL por la de tu repositorio)
2. Sube tu Excel (plantilla en `ejemplo_coordenadas.xlsx`)
3. Descarga el archivo `.kmz`
4. Impórtalo en Google My Maps

## Estructura del Excel
- Columna obligatoria: `Nombre Comercial`
- Opción A: columnas `Latitud` y `Longitud` (números)
- Opción B: columna `Dirección` (texto) + API Key de Google

## Licencia
MIT