import unittest
import os
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from pymongo.errors import ConnectionFailure, ConfigurationError

# ===================== Fonctions utilitaires =====================

def get_mongo_uri() -> str:
    """
    Construit et retourne l'URI de connexion MongoDB
    selon les variables d'environnement définies dans .env
    """
    MONGO_USER = os.environ.get("MONGO_ROOT_USERNAME", "root")
    MONGO_PASS = os.environ.get("MONGO_ROOT_PASSWORD", "root")
    MONGO_HOST = os.environ.get("MONGO_HOST", "mongo_db")
    MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
    MONGO_DB = os.environ.get("MONGO_DB", "healthcareDB")

    return f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"


def get_collection(client: MongoClient, db_name: str, collection_name: str):
    """
    Retourne une collection MongoDB après vérifications :
    - vérifie que la collection existe
    - vérifie qu'elle n'est pas vide
    """
    try:
        db = client[db_name]
        if collection_name not in db.list_collection_names():
            raise RuntimeError(f"La collection '{collection_name}' n'existe pas dans la DB '{db.name}'")
        
        collection = db[collection_name]

        if collection.count_documents({}) == 0:
            raise RuntimeError(f"La collection '{collection_name}' est vide !")

        return collection

    except (ConnectionFailure, ConfigurationError) as e:
        raise RuntimeError(f"Erreur de connexion à MongoDB : {e}")

def load_csv_dataframe() -> pd.DataFrame:
    """Charge le CSV et prépare le DataFrame"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.environ.get("CSV_PATH", os.path.join(BASE_DIR, "../data/healthcare_dataset.csv"))
    df = pd.read_csv(csv_path)
    df.columns = [col.replace(" ", "_") for col in df.columns]
    return df


# ===================== Classe de tests =====================

class TestMigration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialisation de la connexion et des données"""
        # Connexion MongoDB
        MONGO_DB = os.environ.get("MONGO_DB", "healthcareDB")
        MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "patients")

        cls.client = MongoClient(get_mongo_uri())
        cls.collection = get_collection(cls.client, MONGO_DB, MONGO_COLLECTION)
        cls.df = load_csv_dataframe()

    def test_no_null_in_db(self):
        """Aucun champ n'est null dans MongoDB (hors _id)"""
        for doc in self.collection.find():
            self.assertFalse(any(v is None for k, v in doc.items() if k != "_id"))

    def test_types_match(self):
        """Vérifie que les types dans MongoDB correspondent aux types du CSV"""
        doc = self.collection.find_one()
        self.assertIsNotNone(doc, "La collection MongoDB est vide !")

        for col in self.df.columns:
            val = doc.get(col)
            self.assertIsNotNone(val, f"La colonne '{col}' est absente dans MongoDB")
            dtype = self.df[col].dtype

            if pd.api.types.is_integer_dtype(dtype):
                self.assertIsInstance(val, int)
            elif pd.api.types.is_float_dtype(dtype):
                self.assertIsInstance(val, float)
            elif pd.api.types.is_object_dtype(dtype):
                # Vérifie si c'est une date
                if all(self.df[col].str.match(r"\d{4}-\d{2}-\d{2}", na=False)):
                    self.assertIsInstance(val, datetime)
                else:
                    self.assertIsInstance(val, str)

    def test_no_duplicates_in_db(self):
        """Vérifie qu'il n'y a pas de doublons dans MongoDB"""
        seen = set()
        duplicates = []

        for doc in self.collection.find({}, {"_id": 0}):
            t = tuple(sorted(doc.items()))
            if t in seen:
                duplicates.append(doc)
            else:
                seen.add(t)

        if duplicates:
            print("Documents en doublon :")
            for d in duplicates:
                print(d)
            raise AssertionError(f"{len(duplicates)} doublons trouvés.")


# ===================== Script principal =====================

if __name__ == "__main__":
    unittest.main()
