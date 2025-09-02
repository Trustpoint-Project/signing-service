"""Module containing urls for user app."""
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.views import SignUpView, TokenCreateView, TokenListView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='users/signin.html'), name='signin'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('tokens/', TokenListView.as_view(), name='token_list'),
    path('generate-token/', TokenCreateView.as_view(), name='api_token'),
]
