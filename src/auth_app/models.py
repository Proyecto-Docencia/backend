from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ['email']


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    region = models.CharField(max_length=100, blank=True, default='')
    comuna = models.CharField(max_length=100, blank=True, default='')
    telefono = models.CharField(max_length=50, blank=True, default='')
    rut = models.CharField(max_length=20, blank=True, default='')
    direccion = models.CharField(max_length=255, blank=True, default='')
    sede = models.CharField(max_length=100, blank=True, default='')
    facultades = models.JSONField(default=list, blank=True)
    carreras = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"