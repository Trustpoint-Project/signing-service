FROM python:3.12

# Install system dependencies
RUN apt-get update && apt-get install -y \
    apache2 \
    apache2-dev \
    libapache2-mod-wsgi-py3 \
    postgresql-client \
    libpq-dev \
    python3-dev \
    libffi-dev \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /code

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install mod_wsgi

RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

COPY . .

# Set up directories and permissions
RUN mkdir -p /var/www/static /var/www/media && \
    chown -R www-data:www-data /var/www && \
    chmod -R 755 /var/www && \
    chown -R www-data:www-data /code && \
    chmod -R 755 /code

COPY apache/django.conf /etc/apache2/sites-available/000-default.conf

RUN python manage.py collectstatic --noinput

RUN a2enmod wsgi && \
    a2enmod rewrite && \
    a2ensite 000-default

EXPOSE 80

CMD ["apache2ctl", "-D", "FOREGROUND"]