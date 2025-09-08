from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from users.models import PasswordResetToken, LoginAttempt

User = get_user_model()


class AuthenticationAPITest(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='existingpass123'
        )

    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post('/api/users/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        data = self.user_data.copy()
        data['password_confirm'] = 'differentpassword'
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        data = self.user_data.copy()
        data['email'] = 'existing@example.com'
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post('/api/users/login/', {
            'email': 'existing@example.com',
            'password': 'existingpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/api/users/login/', {
            'email': 'existing@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = self.client.post('/api/users/login/', {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_account_lockout(self):
        """Test account lockout after multiple failed attempts"""
        # Make 5 failed login attempts
        for i in range(5):
            response = self.client.post('/api/users/login/', {
                'email': 'existing@example.com',
                'password': 'wrongpassword'
            })
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Refresh user from database
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_account_locked())
        
        # Try login with correct credentials - should fail due to lock
        response = self.client.post('/api/users/login/', {
            'email': 'existing@example.com',
            'password': 'existingpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('locked', response.data['non_field_errors'][0].lower())

    def test_password_reset_request(self):
        """Test password reset request"""
        response = self.client.post('/api/users/password/reset/', {
            'email': 'existing@example.com'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that token was created
        self.assertTrue(
            PasswordResetToken.objects.filter(user=self.user).exists()
        )

    def test_password_reset_confirm(self):
        """Test password reset confirmation"""
        # Create reset token
        reset_token = PasswordResetToken.objects.create(user=self.user)
        
        response = self.client.post('/api/users/password/reset/confirm/', {
            'token': str(reset_token.token),
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify token is marked as used
        reset_token.refresh_from_db()
        self.assertIsNotNone(reset_token.used_at)
        
        # Verify user can login with new password
        response = self.client.post('/api/users/login/', {
            'email': 'existing@example.com',
            'password': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_authenticated(self):
        """Test password change for authenticated user"""
        # Login first
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/users/password/change/', {
            'old_password': 'existingpass123',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/api/users/password/change/', {
            'old_password': 'wrongoldpassword',
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        """Test logout functionality"""
        # Login first to get refresh token
        login_response = self.client.post('/api/users/login/', {
            'email': 'existing@example.com',
            'password': 'existingpass123'
        })
        refresh_token = login_response.data['tokens']['refresh']
        
        # Authenticate and logout
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/users/logout/', {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_access_authenticated(self):
        """Test profile access for authenticated user"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_profile_access_unauthenticated(self):
        """Test profile access for unauthenticated user"""
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_access(self):
        """Test dashboard access for authenticated user"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('stats', response.data)

    def test_security_view(self):
        """Test security information endpoint"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/security/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('account_status', response.data)
        self.assertIn('login_statistics', response.data)

    def test_login_attempt_logging(self):
        """Test that login attempts are properly logged"""
        initial_count = LoginAttempt.objects.count()
        
        # Successful login
        self.client.post('/api/users/login/', {
            'email': 'existing@example.com',
            'password': 'existingpass123'
        })
        
        # Failed login
        self.client.post('/api/users/login/', {
            'email': 'existing@example.com',
            'password': 'wrongpassword'
        })
        
        # Check that attempts were logged
        self.assertEqual(LoginAttempt.objects.count(), initial_count + 2)
        
        # Check success/failure status
        success_attempt = LoginAttempt.objects.filter(success=True).last()
        failed_attempt = LoginAttempt.objects.filter(success=False).last()
        
        self.assertEqual(success_attempt.email, 'existing@example.com')
        self.assertEqual(failed_attempt.email, 'existing@example.com')
        self.assertEqual(success_attempt.user, self.user)


class TokenRefreshTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_token_refresh(self):
        """Test JWT token refresh"""
        # Login to get tokens
        login_response = self.client.post('/api/users/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        refresh_token = login_response.data['tokens']['refresh']
        
        # Refresh token
        response = self.client.post('/api/users/token/refresh/', {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
