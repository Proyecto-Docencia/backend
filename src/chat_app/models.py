from django.conf import settings
from django.db import models


class Chat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chats")
    mensaje_usuario = models.TextField()
    respuesta_ia = models.TextField(blank=True, default="")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self) -> str:
        return f"Chat({self.user_id}) {self.fecha:%Y-%m-%d %H:%M}"
