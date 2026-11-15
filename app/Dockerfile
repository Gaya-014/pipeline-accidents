FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Le code source est monté en volume depuis ./app (voir docker-compose.yml)
