#!/bin/bash
# Script pour créer les utilisateurs MongoDB à partir des variables d'environnement

# Lecture des variables d'environnement (venant des secrets GitHub)
READER_USER=${READER_USER}
READER_PASS=${READER_PASS}
MANAGER_USER=${MANAGER_USER}
MANAGER_PASS=${MANAGER_PASS}
ROOT_USER=${MONGO_ROOT_USERNAME}
ROOT_PASS=${MONGO_ROOT_PASSWORD}
DB_NAME=${MONGO_DATABASE}

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
