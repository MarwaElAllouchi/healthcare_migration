#!/bin/bash

case "$1" in
  migrate)
    echo "🚀 Lancement de la migration réelle..."
    python scripts/migrate_patients.py
    ;;
    
  unit)
    echo "🧪 Lancement des tests unitaires..."
    python -m unittest discover -s tests/unit
    ;;
    
  integration)
    echo "🔗 Lancement des tests d'intégration avec données factices..."
    export MONGO_DB=healthcareDB_test
    export CSV_PATH=tests/data/healthcare_dataset_test.csv
    pytest tests/integration -v
    ;;
    
  all)
    
    
    echo "🧪 Tests unitaires..."
    python -m unittest discover -s tests/unit

    echo "🚀 Migration réelle..."
    python scripts/migrate_patients.py
    
    echo "🔗 Tests d'intégration avec données factices..."
    export MONGO_DB=healthcareDB_test
    export CSV_PATH=tests/data/healthcare_dataset_test.csv
    pytest tests/integration -v
    ;;
    
  *)
    echo "Usage: $0 {migrate|unit|integration|all}"
    exit 1
    ;;
esac
