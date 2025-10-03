import os
import pytest
from scripts.migrate_patients import charger_csv, transformer_records, inserer_records, connecter_mongodb

# ----------------- Fixtures -----------------

@pytest.fixture(scope="module")
def records():
    """Prépare les records depuis le CSV factice pour les tests"""
    CSV_PATH = os.environ.get("CSV_PATH", "tests/data/healthcare_dataset_test.csv")
    df = charger_csv(CSV_PATH)
    return transformer_records(df)

@pytest.fixture(scope="module")
def mongo_collection_with_data(records):
    """Connexion à MongoDB sur une base de test, insertion des records, nettoyage avant et après tests"""
    # Utiliser une DB et collection de test
    os.environ["MONGO_DB"] = "healthcareDB_test"
    os.environ["MONGO_COLLECTION"] = "patients_test"

    collection = connecter_mongodb()
    collection.delete_many({})       # nettoyage avant test
    inserer_records(collection, records)  # insertion unique pour tous les tests
    yield collection
    collection.delete_many({})       # nettoyage après test

# ----------------- Tests d'intégration -----------------

def test_insertion_records(mongo_collection_with_data, records):
    """Vérifie que tous les records sont insérés dans MongoDB"""
    assert mongo_collection_with_data.count_documents({}) == len(records)

def test_no_null_values(mongo_collection_with_data):
    """Vérifie qu'aucun champ (hors _id) n'est null"""
    for doc in mongo_collection_with_data.find():
        assert all(v is not None for k, v in doc.items() if k != "_id")

def test_no_duplicates(mongo_collection_with_data):
    """Vérifie qu'il n'y a pas de doublons dans MongoDB"""
    docs = list(mongo_collection_with_data.find({}, {"_id": 0}))
    seen = [tuple(sorted(d.items())) for d in docs]
    assert len(seen) == len(set(seen))
