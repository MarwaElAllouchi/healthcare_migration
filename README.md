### 🏥 Healthcare Migration Project

Ce projet consiste à migrer des données patients depuis un fichier CSV vers MongoDB, gérer les utilisateurs et rôles MongoDB, et permettre l’export et l’import des données.
Il s’inscrit dans un contexte de scalabilité Big Data pour aider un client à mieux gérer ses données médicales.

### 📂 Structure du projet
healthcare_migration
├── data/
│   └── healthcare_dataset.csv             # Fichier source CSV
├── .init/
│   └── entrypoint.sh                       # Script d'entrée pour Docker
├── scripts/
│   └── migrate_patients.py                 # Script de migration
├── init-scripts/
│   └── init-create-users.sh                # Création des utilisateurs MongoDB
├── tests/
│   ├── unit/
│   │   └── test_unitaire.py                # Tests unitaires
│   ├── integration/
│   │   └── test_migration.py              # Tests d’intégration
│   └── data/
│       └── healthcare_dataset_test.csv    # Données factices pour tests
├── requirements.txt                        # Dépendances Python
├── Dockerfile                              # Image migration
├── docker-compose.yml                       # Compose MongoDB + migration
├── .gitattributes                           # Forcer LF sur les scripts .sh
└── README.md
└──schema_patients.md

### 🎯 Contexte du projet

Nous avons reçu un dataset médical de patients fourni par un client.
Leur système actuel ne permettait plus de gérer efficacement la montée en charge (scalabilité).

Notre solution :

Migrer les données dans une base MongoDB, adaptée au Big Data et scalable horizontalement.

Sécuriser l’accès avec un système d’authentification et des rôles (root, manager, readuser).

Conteneuriser MongoDB et les scripts Python avec Docker.

Automatiser la migration et les tests avec un workflow CI/CD GitHub Actions.


### 🗂️ Schéma d’architecture
         +------------------+
         |  CSV Dataset     |
         | (patients data)  |
         +------------------+
                   |
                   v
       +-----------------------+
       | Migration Container   |
       | (migrate_patients.py) |
       +-----------------------+
                   |
                   v
       +-----------------------+
       |   MongoDB Container   |
       |   (healthcareDB)      |
       +-----------------------+
             /           \
            /             \
+-----------------+   +------------------+
|  manager user   |   |   readuser       |
| read/write base |   | read-only access |
+-----------------+   +------------------+

### 🗃️ Schéma de la base MongoDB

MongoDB stocke les données sous forme de documents JSON-like.

Chaque document représente un patient et chaque champ correspond à une clé avec sa valeur associée.

Exemple de document :

{
  "_id": ObjectId,
  "Name": "Luke Burgess",
  "Age": 34,
  "Gender": "Female",
  "Blood_Type": "A-",
  "Medical_Condition": "Hypertension",
  "Date_of_Admission": ISODate("2021-03-04T00:00:00.000Z"),
  "Doctor": "Justin Moore Jr.",
  "Hospital": "Houston Plc",
  "Insurance_Provider": "Blue Cross",
  "Billing_Amount": 18843.02,
  "Room_Number": 260,
  "Admission_Type": "Elective",
  "Discharge_Date": ISODate("2021-03-14T00:00:00.000Z"),
  "Medication": "Aspirin",
  "Test_Results": "Abnormal"
}

### 🐳 Création et gestion des conteneurs
Conteneur MongoDB

Basé sur mongo:6.

Volume Docker pour persistance (mongo_data).

init-create-users.sh crée automatiquement les utilisateurs (root, manager, readuser).

Conteneur Migration

Dépendances Python dans requirements.txt.

Script migrate_patients.py pour la migration des données.

Tests unitaires (test_unitaire.py) et tests d’intégration (test_migration.py).

# Lancement
docker-compose up -d

# Vérification
docker-compose logs mongo_db
docker-compose logs migration

# Nettoyage
docker-compose down -v

### 🔐 Rôles utilisateurs MongoDB
Rôle	Permissions
root	accès complet (admin)
manager	lecture/écriture sur healthcareDB
readuser	lecture seule sur healthcareDB

Exemple connexion root :

docker exec -it healthcare_migration-mongo_db mongosh -u root -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin

### ⚙️ Variables d’environnement

Exemple .env.example :

MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWOR1d=root
MONGO_DB=healthcareDB
READUSER_PASS=****
MANAGER_PASS =***
CSV_PATH=data/healthcare_dataset.csv
EXPORT_PATH=data/exported_patients.csv


⚠️ .env ne doit pas être commité. Dans GitHub Actions, les valeurs sensibles sont définies comme secrets.

### 🚀 Migration des données

Le script migrate_patients.py :

Nettoie les données

Supprime les doublons

Insère dans MongoDB

Valide types et contraintes

### ✅ Tests

Tests unitaires (test_unitaire.py) :
Vérifie les fonctions de nettoyage et transformation de données avec des valeurs fictives.

Tests d’intégration (test_migration.py) :
Vérifie la migration complète vers MongoDB test (healthcareDB_test) avec CSV factice.
Contrôles :

insertion des données
absence de valeurs null
pas de doublons
lancement de tests:
test unitaire : pytest tests/unit/
test d'integration : pytest tests/integration/

### 💾 Export des données
df = pd.DataFrame(list(collection.find({}, {'_id': 0})))
df.to_csv(EXPORT_PATH, index=False)

### 🔄 Intégration Continue (CI/CD)

GitHub Actions : déclenché à chaque push ou PR

Installe Python, MongoDB, dépendances

Exécute migration + tests unitaires et d’intégration

Variables sensibles injectées via secrets

Extrait workflow.yml :

env:
  MONGO_DB: ${{ secrets.MONGO_DB }}
  MONGO_INITDB_ROOT_USERNAME: ${{ secrets.MONGO_INITDB_ROOT_USERNAME }}
  MONGO_INITDB_ROOT_PASSWORD: ${{ secrets.MONGO_INITDB_ROOT_PASSWORD }}
  READUSER_PASS: ${{ secrets.READUSER_PASS }}
  MANAGER_PASS: ${{ secrets.MANAGER_PASS }}

### 📌 Notes

readuser : lecture seule

Chemins relatifs à la racine du projet

.gitattributes force LF sur .sh

Architecture prête pour déploiement cloud

### 🔗 Références

MongoDB Authentication & Roles

Docker Compose Documentation

PyMongo Documentation

GitHub Actions