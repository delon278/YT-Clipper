# 🎬 YTClipper

Busca, descarga y recorta videos de YouTube desde tu navegador, sin instalar nada complicado.

---

## 🚀 Instalación rápida

### Mac / Linux
1. Descomprime la carpeta `ytclipper`
2. Abre la Terminal en esa carpeta
3. Ejecuta:
   ```bash
   chmod +x iniciar.sh
   ./iniciar.sh
   ```
4. El navegador se abrirá solo en `http://localhost:5050`

### Windows
1. Descomprime la carpeta `ytclipper`
2. Haz doble clic en `iniciar.bat`
3. El navegador se abrirá solo en `http://localhost:5050`

---

## 📦 Requisitos

| Programa | Para qué | Cómo instalar |
|----------|----------|---------------|
| **Python 3.8+** | Ejecutar la app | https://python.org |
| **ffmpeg** | Crear clips | `brew install ffmpeg` (Mac) / `sudo apt install ffmpeg` (Linux) / https://ffmpeg.org (Windows) |

El script instalará automáticamente `flask` y `yt-dlp`.

---

## 🎯 Cómo usar

### 1. Buscar
- Ve a la pestaña **Buscar**
- Escribe el nombre del video
- Haz clic en el botón **↓ Descargar** de cualquier resultado

### 2. Descargar
- Se cambiará automáticamente a la pestaña **Descargar**
- Haz clic en **Descargar MP4**
- Espera a que la barra de progreso llegue al 100%

### 3. Clipear
- Ve a la pestaña **Clipear**
- Selecciona el video descargado
- Ajusta el inicio y fin con los controles o el slider
- Ponle un nombre al clip
- Haz clic en **Crear clip** y descárgalo

---

## 📁 Archivos generados

Los archivos se guardan en tu carpeta de usuario:
- **Descargas:** `~/YTClipper/downloads/`
- **Clips:** `~/YTClipper/clips/`

---

## ❓ Problemas comunes

**"No puedo conectar"** → Asegúrate de que el script está corriendo en la terminal.

**"Error al clipear"** → Instala ffmpeg (ver tabla arriba).

**"Video no disponible"** → Algunos videos tienen restricciones geográficas o de edad.

---

Hecho con ❤️ usando Flask + yt-dlp + ffmpeg
