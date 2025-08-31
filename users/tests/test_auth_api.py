from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):
    def test_register_and_token(self):
        # register
        res = self.client.post("/api/auth/register/", {
            "username": "bob",
            "email": "bob@example.com",
            "password": "pass123456"
        }, format="json")
        self.assertEqual(res.status_code, 201)

        # token
        res = self.client.post("/api/auth/token/", {
            "username": "bob",
            "password": "pass123456"
        }, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)
