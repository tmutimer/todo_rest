from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class AuthTests(APITestCase):

    def create_user(self, email, password):
        '''
        Create a user for testing.
        '''
        url = reverse('register')
        data = {'email': email, 'password': password}
        response = self.client.post(url, data, format='json')
        return response

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
        response = self.create_user('', 'Password1!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_email(self):
        '''
        Test that a user cannot register with an invalid email.
        '''
        response = self.create_user('invalidemail', 'Password1!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_no_password(self):
        '''
        Test that a user cannot register without a password.
        '''
        url = reverse('register')
        data = {'email': 'test@user.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_weak_password(self):
        '''
        Test that a user cannot register with an invalid password.
        '''
        response = self.create_user('short@user.com', 'short1!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.create_user('nonumber@user.com', 'Password!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.create_user('nospecial@user.com', 'Password11')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)