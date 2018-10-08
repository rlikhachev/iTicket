from django.test import TestCase, Client
from user.models import User


class UserTestCase(TestCase):

    def setUp(self):
        self.credentials = {
            'username': 'test_user',
            'password': 'testpsswd'
        }
        User.objects.create_user(**self.credentials)

    def test_login(self):
        response = self.client.post('/auth/login/', self.credentials, follow=True)
        self.assertTrue(response.status_code == 200 and response.data['token'])

    def test_fail_login(self):
        fake_credentials = {
            'username': 'test_fake_user',
            'password': 'testpsswd'
        }
        response = self.client.post('/auth/login/', fake_credentials, follow=True)
        self.assertFalse(response.status_code == 200 and response.data['token'])

    def test_logout(self):
        response1 = self.client.post('/auth/login/', self.credentials, follow=True)
        response = self.client.post('/auth/logout/', self.credentials, follow=True)
        self.assertTrue(response.status_code == 200)

    def test_fake_logout(self):
        response = self.client.post('/auth/logout/', self.credentials, follow=True)
        self.assertFalse(response.status_code == 200)
