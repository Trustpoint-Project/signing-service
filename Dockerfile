FROM python:3.12-slim

# Install Apache and required tools
RUN apt-get update && apt-get install -y \
    apache2 apache2-dev curl build-essential libapache2-mod-wsgi-py3 \
    postgresql-client && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create virtual environment
ENV VIRTUAL_ENV=/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
WORKDIR /code
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

RUN pip install mod_wsgi && \
    mod_wsgi-express install-module > /etc/apache2/mods-available/wsgi.load && \
    a2enmod wsgi

# Copy project code
COPY . .

RUN mkdir -p /var/www/static /var/www/media

ENV DJANGO_SETTINGS_MODULE=django_project.settings
ENV DATABASE_HOST=db
ENV DATABASE_PORT=5432
ENV DATABASE_USER=myuser

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy Apache config
COPY apache/django.conf /etc/apache2/sites-available/000-default.conf

RUN chown -R www-data:www-data /var/www/static /var/www/media /code

# Expose Apache port
EXPOSE 80

# Start Apache in foreground
ENTRYPOINT ["/entrypoint.sh"]
