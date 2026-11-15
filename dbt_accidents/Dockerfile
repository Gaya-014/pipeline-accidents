FROM python:3.12-slim
# git est demandé par "dbt debug" (utile seulement pour télécharger des extensions)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
# versions de dbt fixées pour que le projet fonctionne pareil sur toutes les machines
RUN pip install --no-cache-dir "dbt-core~=1.9.0" "dbt-postgres~=1.9.0"
WORKDIR /dbt
ENV DBT_PROFILES_DIR=/dbt
ENTRYPOINT ["dbt"]
