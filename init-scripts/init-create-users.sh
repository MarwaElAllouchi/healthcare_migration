#!/bin/bash
# Script pour créer les utilisateurs MongoDB à partir des variables d'environnement

# Lecture des utilisateurs et mots de passe depuis les variables d'environnement
READER_USER=${MONGO_USER1:-readerUser}
READER_PASS=${MONGO_PASSWORD1:-reader_pass}
MANAGER_USER=${MONGO_USER2:-managerUser}
MANAGER_PASS=${MONGO_PASSWORD2:-readerwrite_pass}
ROOT_USER=${MONGO_ROOT_USERNAME:-root}
ROOT_PASS=${MONGO_ROOT_PASSWORD:-root}
DB_NAME=${MONGO_DATABASE:-healthcareDB}

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
