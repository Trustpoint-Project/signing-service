"""For Managing App."""

from django.apps import AppConfig


class SignersConfig(AppConfig):
    """Default app configuration for signers."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'signers'
