"""Contains Logic of Form on Add Signer Page."""

from typing import Any, ClassVar

from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from trustpoint_core.oid import AlgorithmIdentifier, NamedCurve

from signers.models import Signer


class SignerForm(ModelForm):
    """Creates Add Signer Form."""

    class Meta:
        model = Signer
        fields: ClassVar = ['unique_name', 'signing_algorithm', 'key_length', 'curve', 'hash_function', 'expires_by']
        widgets: ClassVar = {
            'expires_by': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the SignerForm."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    def clean_unique_name(self) -> str:
        """Ensures unique_name is truly unique, except for current instance in edit mode."""
        unique_name = self.cleaned_data.get('unique_name')
        if not unique_name:
            return unique_name

        qs = Signer.objects.filter(unique_name=unique_name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError('A signer with this name already exists.')

        return unique_name

    def clean(self) -> dict[str, Any]:
        """Cleans and validates form input for algorithm-specific constraints."""
        cleaned_data: dict[str, Any] = super().clean() or {}

        algorithm_oid_str = cleaned_data.get('signing_algorithm')
        key_length = cleaned_data.get('key_length')
        expires_by = cleaned_data.get('expires_by')
        curve_input = cleaned_data.get('curve')

        if not algorithm_oid_str:
            msg = 'Signing algorithm is required.'
            raise ValidationError(msg)

        try:
            algorithm_enum = AlgorithmIdentifier.from_dotted_string(algorithm_oid_str)
        except ValueError:
            msg = f'Invalid algorithm: {algorithm_oid_str}'
            raise ValidationError(msg) from None

        if algorithm_enum.public_key_algo_oid.name == 'ECC':
            if not curve_input:
                raise ValidationError('Curve must be selected for ECC-based algorithms.')

            available_curves = [c.value.ossl_curve_name for c in NamedCurve]
            if curve_input not in available_curves:
                raise ValidationError(f'Invalid ECC curve: {curve_input}')

            cleaned_data['key_length'] = None

        else:
            if not key_length:
                msg = 'Key length must be selected for RSA-based algorithms.'
                raise ValidationError(msg)
            if key_length not in [2048, 3072, 4096]:
                msg = 'Unsupported key length. Choose 2048, 3072, or 4096.'
                raise ValidationError(msg)
            cleaned_data['curve'] = None

        if not expires_by:
            msg = 'Expiration date is required.'
            raise ValidationError(msg)

        return cleaned_data
