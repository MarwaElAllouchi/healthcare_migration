#!/bin/bash
# Script pour créer les utilisateurs MongoDB à partir des variables d'environnement

MONGO_HOST=${MONGO_HOST:-mongo_db}
MONGO_PORT=${MONGO_PORT:-27017}
READER_USER=${READER_USER:-readerUser}
READER_PASS=${READER_PASS:-reader_pass}
MANAGER_USER=${MANAGER_USER:-managerUser}
MANAGER_PASS=${MANAGER_PASS:-manager_pass}
ROOT_USER=${MONGO_ROOT_USERNAME:-root}
ROOT_PASS=${MONGO_ROOT_PASSWORD:-root}
DB_NAME=${DB_NAME:-healthcareDB}

# Root temporaire pour initialisation
TEMP_ROOT_USER=root
TEMP_ROOT_PASS=root

# ⏳ Attente que MongoDB soit prêt avec timeout
echo "⏳ Attente que MongoDB soit prêt..."
START_TIME=$(date +%s)
TIMEOUT=60
while true; do
  if mongosh -u "$TEMP_ROOT_USER" -p "$TEMP_ROOT_PASS" --authenticationDatabase "admin" --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB est prêt."
    break
  fi
  NOW=$(date +%s)
  ELAPSED=$((NOW - START_TIME))
  if [ "$ELAPSED" -ge "$TIMEOUT" ]; then
    echo "❌ MongoDB n'est pas prêt après $TIMEOUT secondes, abandon."
    exit 1
  fi
  sleep 2
done

echo "👤 Création des utilisateurs dans la DB $DB_NAME"

mongosh -u "$TEMP_ROOT_USER" -p "$TEMP_ROOT_PASS" --authenticationDatabase "admin" <<EOF
use $DB_NAME

// Création du root réel
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
