import pandas as pd
import pymongo
import time
from datetime import datetime
import os
from pymongo.errors import ConnectionFailure, ConfigurationError

# ===================== Fonctions utilitaires =====================

def clean_record(record: dict) -> dict:
    """Nettoyage générique basé sur le type des valeurs"""
    cleaned = {}
    for key, value in record.items():
        if pd.isna(value):  # valeur manquante
            cleaned[key] = None
            continue

        if str(value).isdigit():  # entier
            cleaned[key] = int(value)
        elif str(value).replace('.', '', 1).isdigit():  # float
            cleaned[key] = round(float(value), 2)
        elif isinstance(value, str) and "-" in value:  # date
            try:
                cleaned[key] = datetime.strptime(value.strip(), "%Y-%m-%d")
            except Exception:
                cleaned[key] = value.strip()
        else:  # texte générique
            cleaned[key] = str(value).strip().title()
    return cleaned

def nettoyer_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie le DataFrame : doublons, valeurs manquantes et champs vides"""
    if df.duplicated().any():
        print(f"⚠ {df.duplicated().sum()} doublons trouvés et supprimés")
        df = df.drop_duplicates()

    if df.isnull().values.any():
        print(f"⚠ {df.isnull().sum().sum()} valeurs manquantes détectées et supprimées")
        df = df.dropna()

    if (df == '').any().any():
        raise ValueError("Certaines lignes du CSV contiennent des champs vides.")
    return df

def charger_csv(csv_path: str) -> pd.DataFrame:
    """Charge et nettoie un CSV"""
    df = pd.read_csv(csv_path)
    df = nettoyer_dataframe(df)
    # Transformation : nettoyer noms de colonnes (espaces → _)
    df.columns = [col.replace(" ", "_") for col in df.columns]
    return df

def transformer_records(df: pd.DataFrame) -> list:
    """Nettoie chaque enregistrement du DataFrame et retourne une liste de dicts"""
    return [clean_record(record) for record in df.to_dict(orient="records")]

def connecter_mongodb(retries: int = 20, delay: int = 2) -> pymongo.collection.Collection:
    """
    Connexion à MongoDB avec le root et retour de la collection.
    Attend que MongoDB soit prêt avant de continuer.
    
    retries : nombre de tentatives
    delay : délai entre chaque tentative (en secondes)
    """
    MONGO_HOST = os.getenv("MONGO_HOST", "mongo_db")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_DB = os.getenv("MONGO_DB", "healthcareDB")
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "patients")
    MONGO_USER = os.getenv("MONGO_ROOT_USERNAME", "root")
    MONGO_PASS = os.getenv("MONGO_ROOT_PASSWORD", "root")

    MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
    print(f"✅ Connexion  à MongoDB sur {MONGO_URI}")
    for attempt in range(1, retries + 1):
        try:
            client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')  # vérifie que MongoDB répond
            print(f"✅ Connexion réussie à MongoDB sur {MONGO_HOST}:{MONGO_PORT}")
            db = client[MONGO_DB]
            return db[MONGO_COLLECTION]
        except (ConnectionFailure, ConfigurationError) as e:
            print(f"⏳ Tentative {attempt}/{retries} : MongoDB non prête, retry dans {delay}s...")
            time.sleep(delay)
    raise ConnectionFailure(f"❌ Impossible de se connecter à MongoDB après {retries} tentatives.")

def inserer_records(collection: pymongo.collection.Collection, records: list):
    """Vide la collection et insère les nouveaux enregistrements"""
    collection.delete_many({})
    collection.insert_many(records)
    print(f"Import terminé ✅ {len(records)} documents insérés.")

def exporter_collection_csv(collection: pymongo.collection.Collection, export_path: str):
    """Export de la collection MongoDB vers CSV"""
    print(f"📤 Export de la collection '{collection.name}' vers {export_path}...")
    df_export = pd.DataFrame(list(collection.find({}, {'_id': 0})))
    df_export.to_csv(export_path, index=False)
    print("✅ Export terminé.")

# ===================== Script principal =====================

def main():
    CSV_PATH = os.environ.get("CSV_PATH", "../data/healthcare_dataset.csv")
    EXPORT_PATH = os.environ.get("EXPORT_PATH", "data/export_patients.csv")

    df = charger_csv(CSV_PATH)
    records = transformer_records(df)

    print("je suis laaaaaaaaaaaaa",df.shape)
    collection = connecter_mongodb()
    inserer_records(collection, records)
    exporter_collection_csv(collection, EXPORT_PATH)

if __name__ == "__main__":
    main()
