from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        payload = {
            'email':'test@example.com',
            'password':'testpass123',
            'name':'Test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        payload = {
            'email':'test@example.com',
            'password':'testpass123',
            'name':'Test name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        payload = {
            'email':'test@example.com',
            'password':'tes',
            'name':'Test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token(self):
        user_details = {
            'email':'test@example.com',
            'password':'testpass123',
            'name':'Test Name'
        }
        create_user(**user_details)
        payload = {
            'email':user_details['email'],
            'password':user_details['password'],
        }

        res=self.client.get(TOKEN_URL, payload)
        self.assertIn('token',res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        create_user(email='test@example.com',password='pass')
        payload = {'email':'test1@example.com','password':'testpass123'}

        res=self.client.get(TOKEN_URL, payload)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        payload = {'email':'test@example','password':''}
        create_user(**payload)

        res=self.client.get(TOKEN_URL, payload)
        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)       
 

