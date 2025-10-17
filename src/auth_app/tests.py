from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
import json
class TestAuthApp(TestCase):

    def setUp(self):
        self.user_model = get_user_model()
        self.email = "testuser@example.com"
        self.password = "securepassword123"
        # Para AbstractUser, se requiere username
        self.test_user = self.user_model.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.password
        )

    def _post_json(self, name: str, payload: dict):
        return self.client.post(
            reverse(name),
            data=json.dumps(payload),
            content_type='application/json'
        )

    def test_login_view_success(self):
        response = self._post_json('login', {
            'email': self.email,
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())

    def test_login_view_invalid_credentials(self):
        response = self._post_json('login', {
            'email': self.email,
            'password': 'wrong-password'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.json())

    def test_register_view(self):
        response = self._post_json('register', {
            'email': 'newuser@example.com',
            'password': 'newsecurepassword123',
            'name': 'New User'
        })
        # La vista actual devuelve 200 por defecto; validamos creación
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user_model.objects.filter(email='newuser@example.com').exists())

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_recovery_view(self):
        response = self._post_json('password_recovery', {
            'email': self.email
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())

class TestBasic(TestCase):
    def test_basic(self):
        self.assertEqual(1 + 1, 2)


class TestLoginSessionFlow(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.email_a = "usera@example.com"
        self.pass_a = "passA123!"
        self.email_b = "userb@example.com"
        self.pass_b = "passB123!"
        # Crear dos usuarios
        self.user_model.objects.create_user(username=self.email_a, email=self.email_a, password=self.pass_a)
        self.user_model.objects.create_user(username=self.email_b, email=self.email_b, password=self.pass_b)

    def _post_json(self, name: str, payload: dict):
        return self.client.post(reverse(name), data=json.dumps(payload), content_type='application/json')

    def test_login_then_profile_matches_user(self):
        # Login como A
        r = self._post_json('login', {'email': self.email_a, 'password': self.pass_a})
        self.assertEqual(r.status_code, 200)
        # Perfil debe reflejar A
        pr = self.client.get(reverse('profile'))
        self.assertEqual(pr.status_code, 200)
        self.assertEqual(pr.json().get('email'), self.email_a)

    def test_switch_user_same_client(self):
        # Login A
        self.assertEqual(self._post_json('login', {'email': self.email_a, 'password': self.pass_a}).status_code, 200)
        self.assertEqual(self.client.get(reverse('profile')).json().get('email'), self.email_a)
        # Login B en la misma sesión debe reemplazar usuario
        self.assertEqual(self._post_json('login', {'email': self.email_b, 'password': self.pass_b}).status_code, 200)
        self.assertEqual(self.client.get(reverse('profile')).json().get('email'), self.email_b)

    def test_register_then_login_profile_ok(self):
        new_email = 'nuevo@example.com'
        new_pass = 'NuevaPass$123'
        # Registrar
        rr = self._post_json('register', {'email': new_email, 'password': new_pass, 'name': 'Nuevo'})
        self.assertEqual(rr.status_code, 200)
        self.assertTrue(self.user_model.objects.filter(email=new_email).exists())
        # Login
        lr = self._post_json('login', {'email': new_email, 'password': new_pass})
        self.assertEqual(lr.status_code, 200)
        pr = self.client.get(reverse('profile'))
        self.assertEqual(pr.status_code, 200)
        self.assertEqual(pr.json().get('email'), new_email)