FROM python:3.13-slim

# Créer le répertoire de travail
WORKDIR /app

# Copier requirements.txt
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier les scripts dans /app/scripts
COPY scripts/ scripts/
COPY data/ data/
COPY tests/ tests/
COPY .init/ .init/

RUN chmod +x ./.init/entrypoint.sh
# Par défaut, on fait tout (migration + tests)
ENV PYTHONPATH=/app/scripts:$PYTHONPATH
CMD ["bash", "./.init/entrypoint.sh", "all"]
