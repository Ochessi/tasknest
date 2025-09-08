from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .models import PasswordResetToken, LoginAttempt
from .serializers import (
    RegisterSerializer, ProfileSerializer, LoginSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    ChangePasswordSerializer, TokenSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for immediate login after registration
        token_data = TokenSerializer.get_token_for_user(user)
        
        return Response({
            'message': 'Registration successful',
            'tokens': token_data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Custom login view with enhanced security features"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        token_data = TokenSerializer.get_token_for_user(user)
        
        return Response({
            'message': 'Login successful',
            'tokens': token_data
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Logout view that blacklists the refresh token"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Successfully logged out'
            }, status=status.HTTP_200_OK)
        except TokenError:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """Request password reset - sends email with reset token"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Create password reset token
            reset_token = PasswordResetToken.objects.create(user=user)
            
            # Send email (in production, use proper email backend)
            self._send_password_reset_email(user, reset_token)
            
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            pass
        
        return Response({
            'message': 'If your email is registered, you will receive password reset instructions.'
        }, status=status.HTTP_200_OK)
    
    def _send_password_reset_email(self, user, reset_token):
        """Send password reset email"""
        subject = 'TaskNest - Password Reset Request'
        message = f"""
        Hello {user.username},
        
        You have requested a password reset for your TaskNest account.
        
        Your password reset token is: {reset_token.token}
        
        This token will expire in 1 hour.
        
        If you did not request this password reset, please ignore this email.
        
        Best regards,
        TaskNest Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log error in production
            print(f"Failed to send password reset email: {e}")


class PasswordResetConfirmView(APIView):
    """Confirm password reset with token"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reset_token = serializer.validated_data['reset_token']
        new_password = serializer.validated_data['password']
        
        # Reset password
        user = reset_token.user
        user.set_password(new_password)
        user.unlock_account()  # Reset any account locks
        user.save()
        
        # Mark token as used
        reset_token.mark_as_used()
        
        # Invalidate all existing sessions/tokens for security
        RefreshToken.for_user(user)
        
        return Response({
            'message': 'Password has been reset successfully'
        }, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """Change password for authenticated users"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        new_password = serializer.validated_data['new_password']
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile management"""
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class DashboardView(APIView):
    """User dashboard with stats and recent activity"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        from tasks.models import Task
        
        # Task statistics
        tasks = Task.objects.filter(user=user)
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(is_completed=True).count()
        pending_tasks = tasks.filter(is_completed=False).count()
        high_priority_tasks = tasks.filter(priority='High', is_completed=False).count()
        
        # Recent login attempts
        recent_attempts = user.login_attempts.filter(
            timestamp__gte=timezone.now() - timezone.timedelta(days=7)
        )[:5]
        
        return Response({
            'user': ProfileSerializer(user).data,
            'stats': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'high_priority_tasks': high_priority_tasks,
                'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
            },
            'recent_login_attempts': [
                {
                    'timestamp': attempt.timestamp,
                    'ip_address': attempt.ip_address,
                    'success': attempt.success,
                    'user_agent': attempt.user_agent[:100] + '...' if len(attempt.user_agent) > 100 else attempt.user_agent
                }
                for attempt in recent_attempts
            ]
        })


class SecurityView(APIView):
    """Security information and settings"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get login attempt statistics
        total_attempts = user.login_attempts.count()
        failed_attempts = user.login_attempts.filter(success=False).count()
        recent_failed = user.login_attempts.filter(
            success=False,
            timestamp__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        # Get active password reset tokens
        active_reset_tokens = user.password_reset_tokens.filter(
            used_at__isnull=True,
            expires_at__gt=timezone.now()
        ).count()
        
        return Response({
            'account_status': {
                'is_locked': user.is_account_locked(),
                'failed_login_attempts': user.failed_login_attempts,
                'account_locked_until': user.account_locked_until,
                'is_email_verified': user.is_email_verified,
            },
            'login_statistics': {
                'total_login_attempts': total_attempts,
                'failed_login_attempts': failed_attempts,
                'recent_failed_attempts': recent_failed,
                'last_login_ip': user.last_login_ip,
            },
            'security_tokens': {
                'active_password_reset_tokens': active_reset_tokens,
            }
        })
    
    def post(self, request):
        """Security actions like unlocking account (admin only) or clearing login attempts"""
        action = request.data.get('action')
        
        if action == 'clear_failed_attempts':
            request.user.unlock_account()
            return Response({'message': 'Failed login attempts cleared'})
        
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint for authentication service"""
    return Response({
        'status': 'healthy',
        'service': 'authentication',
        'timestamp': timezone.now(),
        'features': [
            'user_registration',
            'jwt_authentication', 
            'password_reset',
            'account_security',
            'login_monitoring'
        ]
    })
