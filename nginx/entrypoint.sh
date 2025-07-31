#!/bin/bash

SSL_DIR="/etc/nginx/ssl"
CERT_FILE="$SSL_DIR/certificate.crt"
KEY_FILE="$SSL_DIR/private.key"
DAYS_VALID=365
SUBJECT="/C=GN/ST=WD/L=SCH/O=Schazwald/CN=Campusnew"

mkdir -p "$SSL_DIR"

if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
  echo "Generating new TLS certificate..."
  openssl req -x509 -nodes -days $DAYS_VALID -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "$SUBJECT"
else
  echo "TLS certificate already exists."
fi

echo "Starting NGINX..."
exec nginx -g "daemon off;"
