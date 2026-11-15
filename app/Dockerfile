FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# le code est monté depuis mon dossier app (voir docker-compose.yml)
