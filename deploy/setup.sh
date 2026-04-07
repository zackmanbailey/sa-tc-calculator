#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
#  SA / TC Calculator — Server Setup Script
#  Run on a fresh Ubuntu 22.04+ server (DigitalOcean Droplet, etc.)
#  Usage:  sudo bash setup.sh  your-domain.com
#  Example: sudo bash setup.sh  calc.titancarports.com
# ──────────────────────────────────────────────────────────────────────
set -euo pipefail

DOMAIN="${1:-}"
APP_DIR="/opt/sa-tc-calculator"
APP_USER="satc"
PORT=8888

if [ -z "$DOMAIN" ]; then
  echo "Usage: sudo bash setup.sh <your-domain>"
  echo "Example: sudo bash setup.sh calc.titancarports.com"
  exit 1
fi

echo "════════════════════════════════════════════════════"
echo "  SA / TC Calculator — Server Setup"
echo "  Domain: $DOMAIN"
echo "════════════════════════════════════════════════════"

# ── 1. System packages ────────────────────────────────────────────────
echo "→ Installing system packages..."
apt update -y
apt install -y python3 python3-pip nginx certbot python3-certbot-nginx unzip curl

# ── 2. Python packages ───────────────────────────────────────────────
echo "→ Installing Python packages..."
pip3 install tornado openpyxl reportlab bcrypt --break-system-packages

# ── 3. App user & directory ──────────────────────────────────────────
echo "→ Setting up app directory..."
id -u $APP_USER &>/dev/null || useradd -r -s /bin/false $APP_USER
mkdir -p $APP_DIR
cp -r /root/combined_calc/* $APP_DIR/ 2>/dev/null || cp -r ./combined_calc/* $APP_DIR/ 2>/dev/null || {
  echo "ERROR: Could not find combined_calc directory."
  echo "Upload your combined_calc folder to /root/ first, then re-run this script."
  exit 1
}
mkdir -p $APP_DIR/data/certs $APP_DIR/data/projects
chown -R $APP_USER:$APP_USER $APP_DIR

# ── 4. Systemd service ──────────────────────────────────────────────
echo "→ Creating systemd service..."
cat > /etc/systemd/system/sa-tc-calc.service << SVCEOF
[Unit]
Description=SA/TC Calculator
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 $APP_DIR/app.py --port $PORT --no-browser --auth
Restart=always
RestartSec=5
Environment=AUTH_ENABLED=1
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable sa-tc-calc
systemctl start sa-tc-calc

echo "→ Waiting for app to start..."
sleep 3
if systemctl is-active --quiet sa-tc-calc; then
  echo "   ✅ App is running on port $PORT"
else
  echo "   ❌ App failed to start. Check: journalctl -u sa-tc-calc -n 50"
  exit 1
fi

# ── 5. Nginx config ─────────────────────────────────────────────────
echo "→ Configuring Nginx..."
cat > /etc/nginx/sites-available/sa-tc-calc << NGXEOF
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }
}
NGXEOF

ln -sf /etc/nginx/sites-available/sa-tc-calc /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

echo "   ✅ Nginx configured for $DOMAIN"

# ── 6. SSL Certificate (Let's Encrypt) ─────────────────────────────
echo "→ Obtaining SSL certificate..."
echo "   (Make sure DNS for $DOMAIN points to this server's IP first!)"
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect || {
  echo ""
  echo "   ⚠️  SSL certificate could not be obtained automatically."
  echo "   This usually means DNS isn't pointed to this server yet."
  echo "   After updating DNS, run:"
  echo "     sudo certbot --nginx -d $DOMAIN"
  echo ""
  echo "   The app is still accessible at http://$DOMAIN (no SSL yet)."
}

# ── 7. Firewall ────────────────────────────────────────────────────
echo "→ Configuring firewall..."
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

# ── Done ────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════"
echo "  ✅  SETUP COMPLETE!"
echo ""
echo "  Your calculator is live at:"
echo "    https://$DOMAIN"
echo ""
echo "  Default logins:"
echo "    admin  /  titan2026"
echo "    brad   /  brad2026"
echo ""
echo "  Admin panel (manage users):"
echo "    https://$DOMAIN/admin"
echo ""
echo "  Useful commands:"
echo "    sudo systemctl restart sa-tc-calc   # restart app"
echo "    sudo systemctl status sa-tc-calc    # check status"
echo "    sudo journalctl -u sa-tc-calc -f    # view live logs"
echo "    sudo certbot renew                  # renew SSL cert"
echo ""
echo "  IMPORTANT: Change the default passwords immediately!"
echo "  Log in as admin → go to /admin → add/update users."
echo "════════════════════════════════════════════════════"
