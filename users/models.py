""" "Database models for user tokens."""

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models



class UserManager(BaseUserManager):
    def create_user(self, subject_dn: str, **extra):
        if not subject_dn:
            raise ValueError('subject_dn is required')
        user = self.model(subject_dn=subject_dn, **extra)
        user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, subject_dn: str, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(subject_dn, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    subject_dn = models.CharField(max_length=1024, unique=True)
    common_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    trust_chain = models.ForeignKey(TrustChain, on_delete=models.PROTECT, null=True, help_text='Allowed issuing chain')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'subject_dn'
    REQUIRED_FIELDS: list[str] = []
    objects = UserManager()

    def __str__(self):
        return self.subject_dn
