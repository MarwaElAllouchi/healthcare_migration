
# ⚠️ Root temporaire (celui défini dans docker-compose / workflow)
TEMP_ROOT_USER=root
TEMP_ROOT_PASS=root

echo "⏳ Attente que MongoDB soit prêt..."
until mongosh -u "$TEMP_ROOT_USER" -p "$TEMP_ROOT_PASS" --authenticationDatabase "admin" --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
  sleep 2
done
echo "✅ MongoDB est prêt."

echo "👤 Création des utilisateurs dans la DB $MONGO_DB"

mongosh -u "$TEMP_ROOT_USER" -p "$TEMP_ROOT_PASS" --authenticationDatabase "admin" <<EOF
use $MONGO_DB

db.createUser({user: "$READER_USER", pwd: "$READER_PASS", roles:["read"]})
db.createUser({user: "$MANAGER_USER", pwd: "$MANAGER_PASS", roles:["readWrite"]})
EOF

echo "✅ Utilisateurs créés avec succès."