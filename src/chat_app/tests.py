from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Chat


class ChatTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="u1", email="u1@example.com", password="pass12345")

    def test_create_and_list_chat(self):
        # login session
        self.client.post(reverse("login"), data={"email": "u1@example.com", "password": "pass12345"})

        # create chat
        resp = self.client.post(reverse("crear_chat"), data={"mensaje_usuario": "Hola"}, content_type="application/json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Chat.objects.filter(user=self.user).count(), 1)

        # list chats
        resp2 = self.client.get(reverse("mis_chats"))
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp2.json().get("results", [])), 1)
