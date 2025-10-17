from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
import json

class TestPlansIsolation(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.email_a = 'a@example.com'
        self.pass_a = 'Aa123456!'
        self.email_b = 'b@example.com'
        self.pass_b = 'Bb123456!'
        self.user_a = self.user_model.objects.create_user(username=self.email_a, email=self.email_a, password=self.pass_a)
        self.user_b = self.user_model.objects.create_user(username=self.email_b, email=self.email_b, password=self.pass_b)

    def _post_json(self, url_name: str, payload: dict):
        return self.client.post(reverse(url_name), data=json.dumps(payload), content_type='application/json')

    def test_plan_list_isolated_by_user(self):
        # Usuario A crea plan
        self.assertEqual(self._post_json('login', {'email': self.email_a, 'password': self.pass_a}).status_code, 200)
        cr = self.client.post(reverse('crear_planificacion'), data=json.dumps({'titulo': 'Plan A', 'descripcion': 'desc', 'contenido': {}}), content_type='application/json')
        self.assertEqual(cr.status_code, 201)
        # Lista A debe tener 1
        lr_a = self.client.get(reverse('mis_planificaciones'))
        self.assertEqual(lr_a.status_code, 200)
        self.assertEqual(len(lr_a.json().get('results', [])), 1)

        # Cambiar a usuario B en la MISMA client session
        self.assertEqual(self._post_json('login', {'email': self.email_b, 'password': self.pass_b}).status_code, 200)
        # Lista B debe estar vacía
        lr_b = self.client.get(reverse('mis_planificaciones'))
        self.assertEqual(lr_b.status_code, 200)
        self.assertEqual(len(lr_b.json().get('results', [])), 0)
