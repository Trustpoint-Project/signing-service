"""Module containing views to handle user signup, token listing, and token creation."""

import secrets
from typing import Any

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, ListView

from users.forms import UserTokenForm
from users.models import UserToken


class SignUpView(FormView):
    """View to handle user signup using Django's UserCreationForm."""

    template_name = 'users/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('signin')

    def form_valid(self, form: UserCreationForm) -> HttpResponse:
        """Process a valid signup form submission.

        Args:
            form: A valid user creation form.

        Returns:
            HttpResponse redirecting to the signin page with a success message.
        """
        form.save()
        messages.success(self.request, 'Signup successful! Please log in.')
        return super().form_valid(form)


class TokenListView(LoginRequiredMixin, ListView):
    """View to display the list of tokens owned by the current user."""

    model = UserToken
    template_name = 'users/token_list.html'
    context_object_name = 'tokens'

    def get_queryset(self) -> Any:
        """Retrieve tokens associated with the logged-in user.

        Args:
            None

        Returns:
            QuerySet of UserToken objects belonging to the current user.
        """
        return UserToken.objects.filter(user=self.request.user)


class TokenCreateView(LoginRequiredMixin, CreateView):
    """View to create new access tokens for the logged-in user."""

    model = UserToken
    form_class = UserTokenForm
    template_name = 'users/token_form.html'
    success_url = reverse_lazy('token_list')

    def form_valid(self, form: UserTokenForm) -> HttpResponse:
        """Process a valid token creation form submission.

        Args:
            form: A valid user token creation form.

        Returns:
            HttpResponse redirecting to the token list page.
        """
        token = form.save(commit=False)
        token.user = self.request.user
        token.key = secrets.token_hex(20)
        token.save()
        return super().form_valid(form)
