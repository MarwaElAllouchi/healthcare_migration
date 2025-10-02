# Lecture des variables d'environnement (venant des secrets GitHub)
DB_NAME="${DB_NAME:-healthcareDB}"
READER_USER="${READER_USER:-readerUser}"
READER_PASS="${READER_PASS:-reader_pass}"
MANAGER_USER="${MANAGER_USER:-managerUser}"
MANAGER_PASS="${MANAGER_PASS:-readerwrite_pass}"

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

db.createUser({user: "$READER_USER", pwd: "$READER_PASS", roles:["read"]})
db.createUser({user: "$MANAGER_USER", pwd: "$MANAGER_PASS", roles:["readWrite"]})
EOF

echo "✅ Utilisateurs créés avec succès."