from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class AuthTests(APITestCase):
    def test_user_registration(self):
        url = reverse('register')
        data = {'email': 'test@user.com', 'password': 'Password1!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)

    def test_user_registration_conflicting_email(self):
        url = reverse('register')
        data = {'email': 'helloagain@user.com', 'password': 'Password1!'}
        first_response = self.client.post(url, data, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        second_response = self.client.post(url, data, format='json')
        print(second_response.data)
        # We already used that email address for an existing user, so it's a conflict
        self.assertEqual(second_response.status_code, status.HTTP_409_CONFLICT)
