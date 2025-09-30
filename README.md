# Healthcare Migration Project

Ce projet consiste à migrer des données patients depuis un fichier CSV vers MongoDB, gérer les utilisateurs et rôles MongoDB, et permettre l’export et l’import des données.

---

## 📂 Structure du projet

healthcare_migration
├── data/
│ └── healthcare_dataset.csv # Fichier source CSV
├── scripts/
│ ├── migrate_patients.py # Script de migration
│ ├── test_migration.py # Tests unitaires
├── init-scripts/
│ └── init_users.js # Création des utilisateurs et rôles MongoDB
├── requirements.txt # Dépendances Python
├── Dockerfile # Image migration
├── docker-compose.yml # Compose MongoDB + migration
└── README.md



## ⚙️ Prérequis

- Docker & Docker Compose  
- Python 3.13  
- pip (pour installer les dépendances si besoin)



## 🐳 Instructions Docker

### 1. Build des images

docker-compose build --no-cache
### 2. Lancer les conteneurs
docker-compose up -d
### 3. Vérifier les logs
docker-compose logs -f migration

## 🔐 Utilisateurs et rôles MongoDB
Dans init-scripts/init_users.js :
root : accès complet (admin)
readerUser : accès lecture seule sur healthcareDB
#### Exemple pour se connecter avec root :
docker exec -it healthcare_migration-mongo_db mongosh -u root -p root --authenticationDatabase admin
#### Exemple pour se connecter en lecture seule :
docker exec -it healthcare_migration-mongo_db mongosh -u readerUser -p readerPass --authenticationDatabase healthcareDB
## 🚀Migration des données
Le script migrate_patients.py :

Supprime les doublons

Insère les données du CSV dans la collection patients

Supporte la connexion avec l’utilisateur root

## Variables d’environnement :
MONGO_HOST : hôte MongoDB (mongo_db dans Docker Compose)

MONGO_PORT : port MongoDB (27017)

MONGO_DB : nom de la base (healthcareDB)

MONGO_COLLECTION : collection (patients)

CSV_PATH : chemin vers le CSV (data/healthcare_dataset.csv)

MONGO_INITDB_ROOT_USERNAME : utilisateur root

MONGO_INITDB_ROOT_PASSWORD : mot de passe root

## ✅ Tests
Le script test_migration.py vérifie :

Aucune valeur null dans MongoDB

Les types correspondent à ceux du CSV

Absence de doublons
python scripts/test_migration.py

## 💾 Export des données
Le projet supporte l’export des données MongoDB vers un fichier CSV.

### Variable :
EXPORT_PATH : chemin du fichier exporté, ex. data/exported_patients.csv

Exemple d’utilisation dans un script Python :

python : 
df = pd.DataFrame(list(collection.find()))
df.to_csv(EXPORT_PATH, index=False)
## 📌 Notes
Assurez-vous que le conteneur MongoDB est démarré avant de lancer la migration.

L’utilisateur readerUser n’a accès qu’en lecture seule.

Les doublons sont automatiquement détectés et supprimés pendant la migration.

Tous les chemins sont relatifs à la racine du projet.

## 🔗 Références
MongoDB Authentication & Roles
Docker Compose Documentation
PyMongo Documentation