#!/bin/bash
export MONGO_COLLECTION_TEST="${MONGO_COLLECTION_TEST:-patients_test}"
export CSV_PATH_TEST="${CSV_PATH_TEST:-/app/data/healthcare_dataset_test.csv}"
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
   
    pytest tests/integration -v
    ;;
    
  all)
    
    
    echo "🧪 Tests unitaires..."
    python -m unittest discover -s tests/unit

    echo "🚀 Migration réelle..."
    python scripts/migrate_patients.py
    
    echo "🔗 Tests d'intégration avec données factices..."
    pytest tests/integration -v
    ;;
    
  *)
    echo "Usage: $0 {migrate|unit|integration|all}"
    exit 1
    ;;
esac
