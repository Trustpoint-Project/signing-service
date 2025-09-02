"""Forms for creating and managing user tokens."""

from datetime import timedelta
from typing import ClassVar

from django import forms
from django.utils import timezone

from .models import UserToken


class UserTokenForm(forms.ModelForm):
    """Form for creating and updating user tokens with an expiration date."""

    expires_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), initial=timezone.now() + timedelta(days=7)
    )

    class Meta:
        """Metadata for UserTokenForm."""

        model = UserToken
        fields: ClassVar[tuple[str]] = ('expires_at',)
