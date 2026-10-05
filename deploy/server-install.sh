#!/usr/bin/env bash
# Runs on the server (called by deploy.ps1). Copies the uploaded site into place
# and enables the Nginx config. Safe to run again for every update.
set -euo pipefail
SRC="$HOME/hormozraya-upload"

echo "==> Copying website files to /var/www/hormozraya"
sudo mkdir -p /var/www/hormozraya
sudo rm -rf /var/www/hormozraya/*
sudo cp -r "$SRC/public/." /var/www/hormozraya/

echo "==> Enabling the Nginx site"
sudo cp "$SRC/nginx-arvan.conf" /etc/nginx/sites-available/hormozraya
sudo ln -sf /etc/nginx/sites-available/hormozraya /etc/nginx/sites-enabled/hormozraya
sudo nginx -t
sudo systemctl reload nginx

code=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: hormozraya.ir" http://127.0.0.1/ || true)
if [ "$code" = "200" ]; then
  echo "==> Done. The server answers for hormozraya.ir (HTTP $code)."
else
  echo "==> Installed, but the local check returned HTTP $code. Check: sudo tail /var/log/nginx/error.log"
fi
