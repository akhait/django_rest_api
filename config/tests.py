from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token
from rest_framework.test import APITestCase

class JWTViewsSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')

    def test_obtain_jwt_token(self):
        '''
        Test POST /auth/
        Should return JWT token for authenticated user
        '''

        # inactive user
        self.user.is_active = False
        self.user.save()
        resp = self.client.post(reverse(obtain_jwt_token), {'username':'testuser', 'password':'pass'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # bad credentials

        # active user
        self.user.is_active = True
        self.user.save()
        resp = self.client.post(reverse(obtain_jwt_token), {'username':'testuser', 'password':'pass'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in resp.data)
        token = resp.data['token']

    def test_verify_jwt_token(self):
        '''
        Test POST /auth/verify/
        Should return JWT token for authenticated user
        '''
        # obtain token
        resp = self.client.post(reverse(obtain_jwt_token), {'username':'testuser', 'password':'pass'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in resp.data)
        token = resp.data['token']

        # bad token
        resp = self.client.post(reverse(verify_jwt_token), {'token': 'abc'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # good token
        resp = self.client.post(reverse(verify_jwt_token), {'token': token})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_refresh_jwt_token(self):
        # obtain token
        resp = self.client.post(reverse(obtain_jwt_token), {'username':'testuser', 'password':'pass'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in resp.data)
        token = resp.data['token']

         # bad token
        resp = self.client.post(reverse(refresh_jwt_token), {'token': 'abc'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # good token
        resp = self.client.post(reverse(refresh_jwt_token), {'token': token})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def tearDown(self):
        self.user.delete()
