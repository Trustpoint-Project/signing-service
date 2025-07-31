FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies, including OpenSSL for SSL generation
RUN apt-get update && apt-get install -y openssl


WORKDIR /code


COPY pyproject.toml uv.lock ./
RUN pip install .

COPY . .




EXPOSE 8080 8081


CMD ["gunicorn", "django_project.wsgi:application", "--bind", "0.0.0.0:8000"]
