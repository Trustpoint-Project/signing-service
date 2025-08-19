"""For Managing App."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Default app configuration for Users."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
