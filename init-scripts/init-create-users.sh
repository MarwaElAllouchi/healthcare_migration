#!/bin/bash
# Script pour créer les utilisateurs MongoDB à partir des variables d'environnement

# Lecture des utilisateurs et mots de passe depuis les variables d'environnement
# Variables d'environnement (venant des secrets GitHub ou defaults)
MONGO_HOST=${MONGO_HOST:-mongo_db}
MONGO_PORT=${MONGO_PORT:-27017}
READER_USER=${READER_USER:-readerUser}
READER_PASS=${READER_PASS:-reader_pass}
MANAGER_USER=${MANAGER_USER:-managerUser}
MANAGER_PASS=${MANAGER_PASS:-manager_pass}
ROOT_USER=${MONGO_ROOT_USERNAME:-root}
ROOT_PASS=${MONGO_ROOT_PASSWORD:-root}
DB_NAME=${DB_NAME:-healthcareDB}

# Root temporaire défini dans le service GitHub Actions
TEMP_ROOT_USER=root
TEMP_ROOT_PASS=root

# Affichage pour debug (optionnel, à retirer en production)
echo "Création des utilisateurs dans la DB $DB_NAME"
echo "READER_USER=$READER_USER"
echo "MANAGER_USER=$MANAGER_USER"

# Création des utilisateurs dans MongoDB
mongosh -u "$ROOT_USER" -p "$ROOT_PASS" --authenticationDatabase "admin" <<EOF
use $DB_NAME

db.createUser({
  user: "$READER_USER",
  pwd: "$READER_PASS",
  roles: [{ role: "read", db: "$DB_NAME" }]
})

db.createUser({
  user: "$MANAGER_USER",
  pwd: "$MANAGER_PASS",
  roles: [{ role: "readWrite", db: "$DB_NAME" }]
})
EOF