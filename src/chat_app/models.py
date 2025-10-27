from django.conf import settings
from django.db import models


class ChatSession(models.Model):
    """Sesión de chat que agrupa mensajes"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_sessions")
    titulo = models.CharField(max_length=200, default="Nueva conversación")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-actualizado_en"]

    def __str__(self) -> str:
        return f"{self.titulo} - {self.user.email}"


class Chat(models.Model):
    """Mensaje individual dentro de una sesión"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="mensajes", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chats")
    mensaje_usuario = models.TextField()
    respuesta_ia = models.TextField(blank=True, default="")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha"]  # Orden cronológico dentro de una sesión

    def __str__(self) -> str:
        return f"Chat({self.user_id}) {self.fecha:%Y-%m-%d %H:%M}"
