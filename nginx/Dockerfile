FROM nginx:latest

RUN apt-get update && apt-get install -y openssl

COPY default.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh
