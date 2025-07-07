import secrets

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse_lazy
from django.contrib import messages

from django.views.generic import FormView, TemplateView, ListView, CreateView

from users.forms import UserTokenForm
from users.models import UserToken


class SignUpView(FormView):
    template_name = 'users/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('signin')

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f"Signup successful! Please log in.")
        return super().form_valid(form)



class TokenListView(LoginRequiredMixin, ListView):
    model = UserToken
    template_name = 'users/token_list.html'
    context_object_name = 'tokens'

    def get_queryset(self):
        return UserToken.objects.filter(user=self.request.user)

class TokenCreateView(LoginRequiredMixin, CreateView):
    model = UserToken
    form_class = UserTokenForm
    template_name = 'users/token_form.html'
    success_url = reverse_lazy('token_list')

    def form_valid(self, form):
        token = form.save(commit=False)
        token.user = self.request.user
        token.key = secrets.token_hex(20)
        token.save()
        return super().form_valid(form)