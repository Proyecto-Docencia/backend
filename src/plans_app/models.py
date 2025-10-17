from django.db import models
from django.conf import settings


class Planificacion(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='planificaciones')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, default='')
    contenido = models.JSONField(default=dict, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-actualizado_en']

    def __str__(self):
        return f"{self.titulo} ({self.owner})"
