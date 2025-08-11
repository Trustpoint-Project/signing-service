"""Forms for creating and managing user tokens."""

from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import UserToken


class UserTokenForm(forms.ModelForm):
    expires_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), initial=timezone.now() + timedelta(days=7)
    )

    class Meta:
        model = UserToken
        fields = ['expires_at']
