"""Database models for user tokens."""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserToken(models.Model):
    """Model representing an authentication token for a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()



    def __str__(self)-> str:
        """To represent the Token object with its user(creator) and its expiration date.

        Returns: Give out Token object its user(Creator) and its expiration date.

        """
        return f'Token for {self.user.username} (exp: {self.expires_at.date()})'

    def is_expired(self) -> bool:
        """Check if the token is expired.

        Returns:
            bool: True if the token's expiration date has passed, otherwise False.
        """
        return timezone.now() > self.expires_at
