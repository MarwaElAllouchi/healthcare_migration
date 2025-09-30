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

# Définir le point d'entrée : migration puis tests
CMD ["bash", "-c", "python scripts/migrate_patients.py && python scripts/test_migration.py"]
