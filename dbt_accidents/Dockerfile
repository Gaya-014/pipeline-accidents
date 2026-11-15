FROM python:3.12-slim
# git est requis par dbt (résolution des dépendances)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
# dbt-core et l'adaptateur sont épinglés pour garantir un comportement identique d'une machine à l'autre
RUN pip install --no-cache-dir "dbt-core~=1.9.0" "dbt-postgres~=1.9.0"
WORKDIR /dbt
ENV DBT_PROFILES_DIR=/dbt
ENTRYPOINT ["dbt"]
