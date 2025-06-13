"""Contains Routes of URls for Signer App at App level."""

from django.urls import path

from . import views
from .views import SignerDelete, SignerList, edit_signer, sign_hash_api

urlpatterns = [
    path('add-signer/', views.add_signer, name='addSigner'),
    path('', SignerList.as_view(), name='signerList'),
    path('delete-signer/<int:pk>/', SignerDelete.as_view(), name='deleteSigner'),
    path('edit-signer/<int:signer_id>/', edit_signer, name='editSigner'),
    path('signer/<int:signer_id>/', views.signer_detail, name='signerDetail'),
    path('api/sign/', sign_hash_api, name='sign_hash_api'),
]
