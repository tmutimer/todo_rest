from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class TestUtils:
        '''
        Utility class to collect repetitive setup tasks.
        '''
        @staticmethod
        def register_user(client, email, password):
            '''
            Create a user for testing.
            '''
            url = reverse('register')
            data = {'email': email, 'password': password}
            response = client.post(url, data, format='json')
            return response

        @staticmethod
        def register_default_test_user(client):
            '''
            Create a test user.
            '''
            return TestUtils.register_user(client, 'test@user.com', 'Password1!')

class AuthTests(APITestCase):

    def test_user_registration(self):
        '''
        Test that a user can register.
        '''
        response = TestUtils.register_default_test_user(self.client)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)

    def test_user_registration_conflicting_email(self):
        '''
        Test that a user cannot register with an email that already exists.
        '''
        first_response = TestUtils.register_default_test_user(self.client)
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        second_response = TestUtils.register_default_test_user(self.client)
        # We already used that email address for an existing user, so it's a bad request.
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_no_email(self):
        '''
        Test that a user cannot register without an email.
        '''
        response = TestUtils.register_user(self.client, '', 'Password1!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_email(self):
        '''
        Test that a user cannot register with an invalid email.
        '''
        response = TestUtils.register_user(self.client, 'invalidemail', 'Password1!')
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
        response = TestUtils.register_user(self.client, 'short@user.com', 'short1!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # At least one number
        response = TestUtils.register_user(self.client, 'nonumber@user.com', 'Password!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # At least one special character
        response = TestUtils.register_user(self.client, 'nospecial@user.com', 'Password11')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Login tests
        
    def test_user_login(self):
        '''
        Test that a user can log in.
        '''
        # First, create a user
        TestUtils.register_default_test_user(self.client)

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
        TestUtils.register_user(self.client, user_data['email'], user_data['password'])

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
        TestUtils.register_default_test_user(self.client)

        url = reverse('login')

        # Try incorrect email
        user_data = {'email': 'void@user.com', 'password': 'Password1!'}
        response = self.client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Try incorrect password
        user_data = {'email': 'test@user.com', 'password': 'wrongpassword'}
        response = self.client.post(url, user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
class TaskTests(APITestCase):
    def setUp(self):
        '''
        Create a user and return their token.
        '''
        user_response = TestUtils.register_default_test_user(self.client)
        self.token = user_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}') 

    def test_create_task(self):
        '''
        Test that a user can create a task
        '''
        url = reverse('tasks')
        task_data = {"name": "Take the bins out"
                     , "description": "Got to be done!"
                     , "due_date": "2024-03-01" }
        response = self.client.post(url, task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in response.data)

    def test_create_task_no_name(self):
        '''
        Test that a task cannot be created without a name
        '''
        url = reverse('tasks')
        task_data = {"description": "Got to be done!"
                     , "due_date": "2024-03-01" }
        response = self.client.post(url, task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_too_long_name(self):
        '''
        Test that a task cannot be created with a name that is too long
        '''
        url = reverse('tasks')
        task_data = {"name": "Take the bins out" * 100
                     , "description": "Got to be done!"
                     , "due_date": "2024-03-01" }
        response = self.client.post(url, task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)