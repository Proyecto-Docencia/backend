from django.test import TestCase, override_settings
from django.urls import reverse
from django.test import Client
import json
from unittest.mock import patch, Mock


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class TestRagProxy(TestCase):
    def setUp(self):
        self.client = Client()

    def _post(self, payload):
        return self.client.post(reverse('query_rag'), data=json.dumps(payload), content_type='application/json')

    def test_missing_question_returns_400(self):
        r = self._post({})
        self.assertEqual(r.status_code, 400)
        self.assertIn('error', r.json())

    @override_settings()
    def test_no_rag_endpoint_returns_500(self):
        # Ensure env var is not set
        with patch('rag_proxy.views.RAG_ENDPOINT', ''):
            r = self._post({'question': 'Hola'})
            self.assertEqual(r.status_code, 500)
            self.assertIn('error', r.json())

    @patch('rag_proxy.views.requests.post')
    def test_successful_proxy_returns_answer(self, mock_post):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'data': ['Respuesta de prueba']}
        mock_post.return_value = mock_resp

        with patch('rag_proxy.views.RAG_ENDPOINT', 'https://example.com'):
            r = self._post({'question': '¿Qué tal?'})
            self.assertEqual(r.status_code, 200)
            self.assertIn('answer', r.json())
            self.assertEqual(r.json()['answer'], 'Respuesta de prueba')
