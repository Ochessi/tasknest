from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from users.models import PasswordResetToken, LoginAttempt

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_creation(self):
        """Test user creation with email as username field"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertFalse(self.user.is_email_verified)
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertIsNone(self.user.account_locked_until)

    def test_account_locking(self):
        """Test account locking functionality"""
        self.assertFalse(self.user.is_account_locked())
        
        # Lock account
        self.user.lock_account(duration_minutes=30)
        self.assertTrue(self.user.is_account_locked())
        
        # Unlock account
        self.user.unlock_account()
        self.assertFalse(self.user.is_account_locked())
        self.assertEqual(self.user.failed_login_attempts, 0)

    def test_failed_login_increment(self):
        """Test failed login attempt tracking"""
        # Increment failed attempts
        for i in range(4):
            self.user.increment_failed_login()
            self.assertEqual(self.user.failed_login_attempts, i + 1)
            self.assertFalse(self.user.is_account_locked())
        
        # Fifth attempt should lock account
        self.user.increment_failed_login()
        self.assertEqual(self.user.failed_login_attempts, 5)
        self.assertTrue(self.user.is_account_locked())


class PasswordResetTokenTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_token_creation(self):
        """Test password reset token creation"""
        token = PasswordResetToken.objects.create(user=self.user)
        
        self.assertEqual(token.user, self.user)
        self.assertIsNotNone(token.token)
        self.assertIsNone(token.used_at)
        self.assertTrue(token.is_valid())

    def test_token_expiration(self):
        """Test token expiration"""
        # Create expired token
        token = PasswordResetToken.objects.create(user=self.user)
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()
        
        self.assertFalse(token.is_valid())

    def test_token_usage(self):
        """Test marking token as used"""
        token = PasswordResetToken.objects.create(user=self.user)
        self.assertTrue(token.is_valid())
        
        token.mark_as_used()
        self.assertFalse(token.is_valid())
        self.assertIsNotNone(token.used_at)


class LoginAttemptTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_attempt_creation(self):
        """Test login attempt logging"""
        attempt = LoginAttempt.objects.create(
            email='test@example.com',
            ip_address='127.0.0.1',
            user_agent='Test Browser',
            success=True,
            user=self.user
        )
        
        self.assertEqual(attempt.email, 'test@example.com')
        self.assertEqual(attempt.ip_address, '127.0.0.1')
        self.assertTrue(attempt.success)
        self.assertEqual(attempt.user, self.user)

    def test_failed_login_attempt(self):
        """Test failed login attempt logging"""
        attempt = LoginAttempt.objects.create(
            email='test@example.com',
            ip_address='127.0.0.1',
            user_agent='Test Browser',
            success=False
        )
        
        self.assertFalse(attempt.success)
        self.assertIsNone(attempt.user)  # No user for failed attempts
