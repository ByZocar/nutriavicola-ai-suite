# Imagen base liviana de Python para el extra (API + dashboard)
FROM python:3.12-slim

# Evita archivos .pyc y fuerza salida sin buffer (mejores logs en contenedor)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Instala dependencias primero para aprovechar la cache de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el codigo y los datos procesados (sin PII real)
COPY src/ ./src/
COPY data/processed/ ./data/processed/

# Render inyecta el puerto en la variable PORT; por defecto usamos 8501
ENV PORT=8501
EXPOSE 8501

# Comando por defecto: el dashboard. La API se levanta con otro comando (ver compose).
CMD streamlit run src/nutria_ai/dashboard/app.py \
    --server.port=${PORT} --server.address=0.0.0.0
