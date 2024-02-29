from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class AuthTests(APITestCase):
    def test_user_registration(self):
        '''
        Test that a user can register.
        '''
        url = reverse('register')
        data = {'email': 'test@user.com', 'password': 'Password1!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)

    def test_user_registration_conflicting_email(self):
        '''
        Test that a user cannot register with an email that already exists.
        '''
        url = reverse('register')
        data = {'email': 'helloagain@user.com', 'password': 'Password1!'}
        first_response = self.client.post(url, data, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        second_response = self.client.post(url, data, format='json')
        # We already used that email address for an existing user, so it's a bad request.
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_no_email(self):
        '''
        Test that a user cannot register without an email.
        '''
        url = reverse('register')
        data = {'password': 'Password1!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_no_password(self):
        '''
        Test that a user cannot register without a password.
        '''
        url = reverse('register')
        data = {'email': 'test@user.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)