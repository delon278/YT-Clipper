FROM python:3.11-slim

# Instalar ffmpeg y dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la app
COPY . .

# Crear carpetas de trabajo (en /tmp para Render, que no tiene disco persistente)
RUN mkdir -p /tmp/YTClipper/downloads /tmp/YTClipper/clips

# Puerto que usa la app
EXPOSE 10000

# Arrancar con gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "2", "--timeout", "300", "app:app"]
