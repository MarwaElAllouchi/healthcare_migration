#!/bin/bash
# Script pour créer les utilisateurs MongoDB à partir des variables d'environnement

# Lecture des variables d'environnement (venant des secrets GitHub)
READER_USER=${MONGO_USER1:-readerUser}
READER_PASS=${MONGO_PASSWORD1:-reader_pass}
MANAGER_USER=${MONGO_USER2:-managerUser}
MANAGER_PASS=${MONGO_PASSWORD2:-readerwrite_pass}
ROOT_USER=${MONGO_ROOT_USERNAME:-rootuser}
ROOT_PASS=${MONGO_ROOT_PASSWORD:-rootpass}
DB_NAME=${MONGO_DATABASE:-healthcareDB}

# ⚠️ Root temporaire (celui défini dans docker-compose / workflow)
TEMP_ROOT_USER=root
TEMP_ROOT_PASS=root

echo "⏳ Attente que MongoDB soit prêt..."
until mongosh -u "$TEMP_ROOT_USER" -p "$TEMP_ROOT_PASS" --authenticationDatabase "admin" --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
  sleep 2
done
echo "✅ MongoDB est prêt."

echo "👤 Création des utilisateurs dans la DB $DB_NAME"

mongosh -u "$TEMP_ROOT_USER" -p "$TEMP_ROOT_PASS" --authenticationDatabase "admin" <<EOF
use $DB_NAME

// Création du root "réel" défini via secrets
db.getSiblingDB("admin").createUser({
  user: "$ROOT_USER",
  pwd: "$ROOT_PASS",
  roles: [ { role: "root", db: "admin" } ]
})

// Utilisateur lecteur
db.createUser({
  user: "$READER_USER",
  pwd: "$READER_PASS",
  roles: [{ role: "read", db: "$DB_NAME" }]
})

// Utilisateur manager
db.createUser({
  user: "$MANAGER_USER",
  pwd: "$MANAGER_PASS",
  roles: [{ role: "readWrite", db: "$DB_NAME" }]
})
EOF

echo "✅ Utilisateurs créés avec succès."
