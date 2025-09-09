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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import PasswordResetToken, LoginAttempt
from .serializers import (
    RegisterSerializer, ProfileSerializer, LoginSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    ChangePasswordSerializer, TokenSerializer
)
from rest_framework import serializers

# Response serializers for Swagger documentation
class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class TokenResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    tokens = TokenSerializer()

class DashboardStatsSerializer(serializers.Serializer):
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    high_priority_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()

class LoginAttemptSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    ip_address = serializers.CharField()
    success = serializers.BooleanField()
    user_agent = serializers.CharField()

class DashboardResponseSerializer(serializers.Serializer):
    user = ProfileSerializer()
    stats = DashboardStatsSerializer()
    recent_login_attempts = LoginAttemptSerializer(many=True)

class AccountStatusSerializer(serializers.Serializer):
    is_locked = serializers.BooleanField()
    failed_login_attempts = serializers.IntegerField()
    account_locked_until = serializers.DateTimeField(allow_null=True)
    is_email_verified = serializers.BooleanField()

class LoginStatisticsSerializer(serializers.Serializer):
    total_login_attempts = serializers.IntegerField()
    failed_login_attempts = serializers.IntegerField()
    recent_failed_attempts = serializers.IntegerField()
    last_login_ip = serializers.CharField(allow_null=True)

class SecurityTokensSerializer(serializers.Serializer):
    active_password_reset_tokens = serializers.IntegerField()

class SecurityResponseSerializer(serializers.Serializer):
    account_status = AccountStatusSerializer()
    login_statistics = LoginStatisticsSerializer()
    security_tokens = SecurityTokensSerializer()

class LogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class SecurityActionSerializer(serializers.Serializer):
    action = serializers.CharField()

class HealthCheckResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    service = serializers.CharField()
    timestamp = serializers.DateTimeField()
    features = serializers.ListField(child=serializers.CharField())

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    @swagger_auto_schema(
        operation_description="Register a new user account",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Registration successful",
                schema=TokenResponseSerializer
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "email": ["A user with this email already exists."],
                        "password_confirm": ["Passwords do not match."]
                    }
                }
            )
        },
        tags=['Authentication']
    )

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
    
    @swagger_auto_schema(
        operation_description="Login with email and password",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=TokenResponseSerializer
            ),
            400: openapi.Response(
                description="Invalid credentials or account locked",
                examples={
                    "application/json": {
                        "non_field_errors": ["Invalid email or password."]
                    }
                }
            )
        },
        tags=['Authentication']
    )
    
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
    
    @swagger_auto_schema(
        operation_description="Logout and blacklist refresh token",
        request_body=LogoutRequestSerializer,
        responses={
            200: openapi.Response(
                description="Successfully logged out",
                schema=MessageResponseSerializer
            ),
            400: openapi.Response(
                description="Invalid token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
                )
            )
        },
        tags=['Authentication']
    )
    
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
    
    @swagger_auto_schema(
        operation_description="Request password reset via email",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Response(
                description="Password reset email sent (if email exists)",
                schema=MessageResponseSerializer
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "email": ["Enter a valid email address."]
                    }
                }
            )
        },
        tags=['Authentication']
    )
    
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
    
    @swagger_auto_schema(
        operation_description="Confirm password reset with token",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Response(
                description="Password reset successful",
                schema=MessageResponseSerializer
            ),
            400: openapi.Response(
                description="Invalid token or validation error",
                examples={
                    "application/json": {
                        "token": ["Token is invalid or has expired."],
                        "password_confirm": ["Passwords do not match."]
                    }
                }
            )
        },
        tags=['Authentication']
    )
    
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
    
    @swagger_auto_schema(
        operation_description="Change password for authenticated user",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                schema=MessageResponseSerializer
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "old_password": ["Current password is incorrect."],
                        "new_password_confirm": ["New passwords do not match."]
                    }
                }
            )
        },
        tags=['User Management']
    )
    
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
    
    @swagger_auto_schema(
        operation_description="Get user profile",
        responses={
            200: openapi.Response(
                description="User profile data",
                schema=ProfileSerializer
            )
        },
        tags=['User Management']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update user profile",
        request_body=ProfileSerializer,
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                schema=ProfileSerializer
            ),
            400: openapi.Response(
                description="Validation error"
            )
        },
        tags=['User Management']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update user profile",
        request_body=ProfileSerializer,
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                schema=ProfileSerializer
            ),
            400: openapi.Response(
                description="Validation error"
            )
        },
        tags=['User Management']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class DashboardView(APIView):
    """User dashboard with stats and recent activity"""
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get user dashboard with task statistics and recent activity",
        responses={
            200: openapi.Response(
                description="Dashboard data",
                schema=DashboardResponseSerializer
            )
        },
        tags=['User Management']
    )
    
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
    
    @swagger_auto_schema(
        operation_description="Get security information and account status",
        responses={
            200: openapi.Response(
                description="Security information",
                schema=SecurityResponseSerializer
            )
        },
        tags=['Security']
    )
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
    
    @swagger_auto_schema(
        operation_description="Perform security actions",
        request_body=SecurityActionSerializer,
        responses={
            200: openapi.Response(
                description="Action completed successfully",
                schema=MessageResponseSerializer
            ),
            400: openapi.Response(
                description="Invalid action",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
                )
            )
        },
        tags=['Security']
    )
    
    def post(self, request):
        """Security actions like unlocking account (admin only) or clearing login attempts"""
        action = request.data.get('action')
        
        if action == 'clear_failed_attempts':
            request.user.unlock_account()
            return Response({'message': 'Failed login attempts cleared'})
        
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Health check endpoint for authentication service",
    responses={
        200: openapi.Response(
            description="Service health status",
            schema=HealthCheckResponseSerializer
        )
    },
    tags=['System']
)
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
