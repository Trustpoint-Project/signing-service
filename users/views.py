"""Views for user signup and token management."""

import secrets

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, ListView

from users.forms import UserTokenForm
from users.models import UserToken


class SignUpView(FormView):
    """Handle user signup of a new user."""

    template_name = 'users/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('signin')

    def form_valid(self, form: UserCreationForm) -> HttpResponse:
        """Save the new user and show a success message.

        Args:
            form (UserCreationForm): The validated user creation form.

        Returns:
            HttpResponse: Redirect to the signin page.
        """
        form.save()
        messages.success(self.request, 'Signup successful! Please log in.')
        return super().form_valid(form)


class TokenListView(LoginRequiredMixin, ListView):
    """Display a list of tokens belonging to the logged-in user."""

    model = UserToken
    template_name = 'users/token_list.html'
    context_object_name = 'tokens'

    def get_queryset(self) -> QuerySet:
        """Return tokens for the current user.

        Returns:
            QuerySet[UserToken]: Tokens belonging to the logged-in user.
        """
        return UserToken.objects.filter(user=self.request.user)


class TokenCreateView(LoginRequiredMixin, CreateView):
    """Allow the logged-in user to create a new token."""

    model = UserToken
    form_class = UserTokenForm
    template_name = 'users/token_form.html'
    success_url = reverse_lazy('token_list')

    def form_valid(self, form: UserTokenForm) -> HttpResponse:
        """Creates a new toke for the user who is requesting the token.

        Args:
            form:User Token form.

        Returns:
            HTTPResponse containing the UserToken object.
        """
        token = form.save(commit=False)
        token.user = self.request.user
        token.key = secrets.token_hex(20)
        token.save()
        return super().form_valid(form)
