#!/bin/bash
set -e

echo "=== 1. Actualizando repositorio ==="
cd /var/www/biblioteca_api
git pull origin main

echo "=== 2. Activando entorno virtual y ejecutando seed ==="
source .venv/bin/activate
python seed.py

echo "=== 3. Configurando servicio systemd ==="
sudo bash -c 'cat << "EOF" > /etc/systemd/system/biblioteca-api.service
[Unit]
Description=API REST Sistema Bibliotecario FastAPI
After=network.target mysql.service
Requires=mysql.service

[Service]
Type=simple
User=azureuser
Group=azureuser
WorkingDirectory=/var/www/biblioteca_api
EnvironmentFile=/var/www/biblioteca_api/.env
Environment=PYTHONUNBUFFERED=1
ExecStart=/var/www/biblioteca_api/.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips=127.0.0.1
Restart=on-failure
RestartSec=5
UMask=0077

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable --now biblioteca-api
sudo systemctl restart biblioteca-api

echo "=== 4. Configurando Nginx ==="
sudo bash -c 'cat << "EOF" > /etc/nginx/sites-available/biblioteca-api
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF'

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/biblioteca-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

echo "=========================================="
echo " ¡DESPLIEGUE FINALIZADO CON ÉXITO! "
echo " Entra en tu navegador a: "
echo " http://68.211.150.191/docs "
echo "=========================================="
