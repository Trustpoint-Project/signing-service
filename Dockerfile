FROM python:3.12-slim

# Install Apache and required tools
RUN apt-get update && apt-get install -y \
    apache2 apache2-dev curl build-essential libapache2-mod-wsgi-py3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create virtual environment
ENV VIRTUAL_ENV=/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
WORKDIR /code
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project code
COPY . .

# Copy Apache config
COPY apache/django.conf /etc/apache2/sites-available/000-default.conf

# Enable WSGI module
RUN a2enmod wsgi

# Expose Apache port
EXPOSE 80

# Start Apache in foreground
CMD ["apache2ctl", "-D", "FOREGROUND"]
