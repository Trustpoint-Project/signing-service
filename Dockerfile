FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install required packages
RUN apt-get update && apt-get install -y nginx openssl

WORKDIR /code

# Install uv and sync dependencies
COPY pyproject.toml uv.lock ./
RUN pip install .

# Activate .venv for following commands (make this default shell env)

# Copy project files
COPY . .

# Copy NGINX config
COPY nginx/default.conf /etc/nginx/nginx.conf

# SSL directory setup
RUN mkdir -p /etc/nginx/ssl

# Collect static files (Django is now available in .venv/bin/python)



# Entrypoint Script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080 8081

ENTRYPOINT ["/entrypoint.sh"]
