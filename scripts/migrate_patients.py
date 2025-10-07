import pandas as pd
import pymongo
import time
from datetime import datetime
import os
from pymongo.errors import ConnectionFailure, ConfigurationError
from pprint import pprint


# =============Essayer d'importer python-dotenv (pour local)=============
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
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

def connecter_mongodb(
    retries: int = 20,
    delay: int = 2,
    env_suffix: str = ""  # ex: "_TEST" pour base de test
) -> pymongo.collection.Collection:
    """
    Connexion à MongoDB, compatible local (.env), Docker et GitHub Actions.
    """

    # Charger le .env local si disponible
    if DOTENV_AVAILABLE and os.path.exists(".env"):
        load_dotenv(override=False)
        print("📄 Fichier .env chargé (en local)")
    elif not DOTENV_AVAILABLE:
        print("⚠️ python-dotenv non installé, variables système utilisées uniquement")

    # Fonction pour lire une variable avec suffixe
    def env(var_name, default=None):
        return os.getenv(f"{var_name}{env_suffix}", default)

    # Variables communes (identiques prod/test)
    host = os.getenv("MONGO_HOST", "mongo_db")
    port = int(os.getenv("MONGO_PORT", 27017))
    username = os.getenv("MONGO_ROOT_USERNAME", "root")
    password = os.getenv("MONGO_ROOT_PASSWORD", "root")
    
    # Variables spécifiques (différentes si _TEST)
    db_name = env("MONGO_DB", "healthcareDB")
    collection_name = env("MONGO_COLLECTION", "patients")

    # Construction URI
    mongo_uri = f"mongodb://{username}:{password}@{host}:{port}/{db_name}?authSource=admin"
    print(f"🔄 Tentative de connexion à MongoDB : {mongo_uri}")

    # Tentatives de connexion
    for attempt in range(1, retries + 1):
        try:
            client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
            print(f"✅ Connexion réussie à MongoDB ({host}:{port})")
            db = client[db_name]
            return db[collection_name]
        except (ConnectionFailure, ConfigurationError) as e:
            print(f"⏳ Tentative {attempt}/{retries} : MongoDB non prête ({e}), retry dans {delay}s...")
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

def crud_examples(collection: pymongo.collection.Collection): 
    
    # --- CREATE ---
    collection.delete_many({})
    print(f"=================Crud Exempels===================")
    
    patient = {
        "Name":"Test Test",
        "Age": 45,
        "Gender": "Male",
        "Blood_Type": "Hypertension",
        "Medical_Condition": 'Hypertension',
        "Doctor": "Justin Moore Jr.",
        "Hospital": 'Houston Plc Test '
        }
    result = collection.insert_one(patient)
    print(f"Patient inséré avec _id: {result.inserted_id}")
    # --- READ ---
    # Lire un patient spécifique
    patient_lu = collection.find_one({"Name":"Test Test"})
    print("Patient trouvé :")
    pprint(patient_lu)

    # Lire plusieurs patients
    for p in collection.find({"Age": {"$gt": 40}}):
      print("Patient > 40 ans :")
      pprint(p)
    # --- UPDATE ---
    result_update = collection.update_one(
        {"Name":"Test Test"},
        {"$set": {"Medical_Condition":"Diabète"}}
    )
    print(f"Documents modifiés : {result_update.modified_count}")

    # --- DELETE ---
    result_delete = collection.delete_one({"Name":"Test Test"})
    print(f"Documents supprimés : {result_delete.deleted_count}")


    print(f"=================Fin Crud Exempels===================")

# ===================== Script principal =====================

def main():
    CSV_PATH = os.getenv("CSV_PATH", "data/healthcare_dataset.csv")
    EXPORT_PATH = os.getenv("EXPORT_PATH", "data/export_patients.csv")

    df = charger_csv(CSV_PATH)
    records = transformer_records(df)

    collection = connecter_mongodb()
    crud_examples(collection)
    inserer_records(collection, records)
    exporter_collection_csv(collection, EXPORT_PATH)

if __name__ == "__main__":
    main()
