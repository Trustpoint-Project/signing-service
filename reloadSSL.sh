#!/bin/bash

# === Configuration ===
SSL_DIR="/etc/nginx/ssl"
CERT_FILE="$SSL_DIR/certificate.crt"
KEY_FILE="$SSL_DIR/private.key"
DAYS_VALID=365
SUBJECT="/C=GN/ST=WD/L=SCH/O=Schazwald/CN=Campusnew"

#Create SSL directory if missing
sudo mkdir -p "$SSL_DIR"


echo "Generating new self-signed SSL certificate..."
sudo openssl req -x509 -nodes -days $DAYS_VALID -newkey rsa:2048 \
  -keyout "$KEY_FILE" \
  -out "$CERT_FILE" \
  -subj "$SUBJECT"

echo "Certificate and key generated at:"
echo "  $CERT_FILE"
echo "  $KEY_FILE"

# Test NGINX config
echo "Testing NGINX configuration..."
if ! sudo nginx -t; then
  echo "NGINX config test failed. Aborting."
  exit 1
fi
echo "NGINX config is valid."

# Reload NGINX
echo "Reloading NGINX to apply new certificate..."
sudo nginx -s reload
echo "NGINX reloaded."

# Show Certificate Details
echo "Loaded certificate info:"
openssl x509 -in "$CERT_FILE" -noout -subject -issuer -dates
