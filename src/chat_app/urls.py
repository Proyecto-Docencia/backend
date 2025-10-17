from django.urls import path
from .views import mis_chats, crear_chat

urlpatterns = [
    path("mis/", mis_chats, name="mis_chats"),
    path("crear/", crear_chat, name="crear_chat"),
]
