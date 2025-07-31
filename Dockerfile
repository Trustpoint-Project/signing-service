FROM python:3.12-slim

# Set environment variables to prevent .pyc file creation and buffer output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies, including OpenSSL for SSL generation
RUN apt-get update && apt-get install -y openssl

# Set working directory to /code
WORKDIR /code
RUN mkdir -p /etc/nginx/ssl/ && \
    openssl genpkey -algorithm RSA -out /etc/nginx/ssl/private.key && \
    openssl req -new -key /etc/nginx/ssl/private.key -out /etc/nginx/ssl/certificate.csr -subj "/CN=localhost" && \
    openssl x509 -req -in /etc/nginx/ssl/certificate.csr -signkey /etc/nginx/ssl/private.key -out /etc/nginx/ssl/certificate.crt

# Copy the dependency files and install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install .

# Copy the entire project
COPY . .


# Generate SSL Certificates

EXPOSE 8080 8081

# Expose port 8000 for Gunicorn
CMD ["gunicorn", "django_project.wsgi:application", "--bind", "0.0.0.0:8000"]
