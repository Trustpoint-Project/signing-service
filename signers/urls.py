"""Contains Routes of URls for Signer App at App level."""

from django.urls import path

from .views import SignerCreate, SignerDelete, SignerDetail, SignerEdit, SignerList, SignHashAPIView

urlpatterns = [
    path('add-signer/', SignerCreate.as_view(), name='addSigner'),
    path('', SignerList.as_view(), name='signerList'),
    path('delete-signer/<int:pk>/', SignerDelete.as_view(), name='deleteSigner'),
    path('edit-signer/<int:pk>/', SignerEdit.as_view(), name='editSigner'),
    path('signer/<int:pk>/', SignerDetail.as_view(), name='signerDetail'),
    path('api/sign/', SignHashAPIView.as_view(), name='sign_hash_api'),
]
