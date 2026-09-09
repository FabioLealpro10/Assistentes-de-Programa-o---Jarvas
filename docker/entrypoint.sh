#!/bin/bash
set -e

echo "Aguardando MySQL em ${DB_HOST:-db}..."
python << 'EOF'
import os
import sys
import time

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "3306"))
user = os.environ.get("DB_USER", "root")
password = os.environ.get("DB_PASSWORD", "jarvas123")
database = os.environ.get("DB_NAME", "IA_JARVAS")

for attempt in range(30):
    try:
        import MySQLdb
        MySQLdb.connect(host=host, port=port, user=user, passwd=password, db=database)
        print("MySQL disponível!")
        sys.exit(0)
    except Exception as exc:
        print(f"Tentativa {attempt + 1}/30: {exc}")
        time.sleep(2)

print("MySQL não respondeu a tempo.")
sys.exit(1)
EOF

echo "Executando migrations..."
python manage.py migrate --noinput

echo "Iniciando servidor JARVAS..."
exec python manage.py runserver 0.0.0.0:8000
