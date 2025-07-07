from django import forms
from .models import UserToken
from django.utils import timezone
from datetime import timedelta

class UserTokenForm(forms.ModelForm):
    expires_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=timezone.now() + timedelta(days=7)
    )

    class Meta:
        model = UserToken
        fields = ['expires_at']
