from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class AuthTests(APITestCase):

    def register_user(self, email, password):
        '''
        Create a user for testing.
        '''
        url = reverse('register')
        data = {'email': email, 'password': password}
        response = self.client.post(url, data, format='json')
        return response
    
    def register_default_test_user(self):
        '''
        Create a test user.
        '''
        return self.register_user('test@user.com', 'Password1!')

    def test_user_registration(self):
        '''
        Test that a user can register.
        '''
        response = self.register_default_test_user()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)

    def test_user_registration_conflicting_email(self):
        '''
        Test that a user cannot register with an email that already exists.
        '''
        first_response = self.register_default_test_user()
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        second_response = self.register_default_test_user()
        # We already used that email address for an existing user, so it's a bad request.
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_no_email(self):
        '''
        Test that a user cannot register without an email.
        '''
        response = self.register_user('', 'Password1!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_email(self):
        '''
        Test that a user cannot register with an invalid email.
        '''
        response = self.register_user('invalidemail', 'Password1!')
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

        # Minimum 8 characters
        response = self.register_user('short@user.com', 'short1!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # At least one number
        response = self.register_user('nonumber@user.com', 'Password!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # At least one special character
        response = self.register_user('nospecial@user.com', 'Password11')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Login tests
        
    def test_user_login(self):
        '''
        Test that a user can log in.
        '''
        # First, create a user
        self.register_default_test_user()

        # Then, log in
        url = reverse('login')
        # Same details as created user
        user_data = {'email': 'test@user.com', 'password': 'Password1!'}
        response = self.client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    def test_user_login_repeated(self):
        '''
        Test that a user can log in multiple times.
        '''
        # First, create a user
        user_data = {'email': 'test@user.com', 'password': 'Password1!'}
        self.register_user(user_data['email'], user_data['password'])

        # Then, log in and check it works on repeated attempts
        url = reverse('login')
        response = self.client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        response = self.client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        response = self.client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        
    def test_user_login_invalid(self):
        '''
        Test that a user cannot log in with invalid credentials.
        '''
        # First, create a user
