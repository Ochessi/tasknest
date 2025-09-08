from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PasswordResetToken, LoginAttempt

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password_confirm"]

    def validate_email(self, value):
        """Validate email is unique and properly formatted"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        """Validate password confirmation and strength"""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        
        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')  # Remove confirmation field
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        request = self.context.get('request')
        
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Log failed attempt
            self._log_login_attempt(email, request, False)
            raise serializers.ValidationError("Invalid email or password.")
        
        # Check if account is locked
        if user.is_account_locked():
            raise serializers.ValidationError(
                "Account is temporarily locked due to multiple failed login attempts. "
                "Please try again later."
            )
        
        # Authenticate user
        user = authenticate(request=request, username=email, password=password)
        if not user:
            # Increment failed attempts for existing user
            try:
                existing_user = User.objects.get(email=email)
                existing_user.increment_failed_login()
            except User.DoesNotExist:
                pass
            
            self._log_login_attempt(email, request, False)
            raise serializers.ValidationError("Invalid email or password.")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        
        # Successful login - reset failed attempts and update login info
        user.unlock_account()
        user.last_login_ip = self._get_client_ip(request)
        user.save(update_fields=['last_login_ip'])
        
        self._log_login_attempt(email, request, True, user)
        
        attrs['user'] = user
        return attrs
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        if not request:
            return None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_login_attempt(self, email, request, success, user=None):
        """Log login attempt for security monitoring"""
        if not request:
            return
        
        LoginAttempt.objects.create(
            email=email,
            ip_address=self._get_client_ip(request) or '0.0.0.0',
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=success,
            user=user
        )


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """Validate that user with this email exists"""
        email = value.lower()
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            pass
        return email


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        token = attrs.get('token')
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        
        # Validate password strength
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        
        # Validate token
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            if not reset_token.is_valid():
                raise serializers.ValidationError({"token": "Token is invalid or has expired."})
            attrs['reset_token'] = reset_token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid token."})
        
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        user = self.context['request'].user
        
        # Check old password
        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Current password is incorrect."})
        
        # Check new password confirmation
        if new_password != new_password_confirm:
            raise serializers.ValidationError({"new_password_confirm": "New passwords do not match."})
        
        # Validate new password strength
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})
        
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    login_attempts_count = serializers.SerializerMethodField()
    last_successful_login = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "date_joined", "is_email_verified",
            "last_login_ip", "failed_login_attempts", "login_attempts_count",
            "last_successful_login"
        ]
        read_only_fields = [
            "id", "date_joined", "last_login_ip", "failed_login_attempts",
            "login_attempts_count", "last_successful_login"
        ]
    
    def get_login_attempts_count(self, obj):
        """Get count of recent login attempts"""
        return obj.login_attempts.filter(
            timestamp__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
    
    def get_last_successful_login(self, obj):
        """Get last successful login timestamp"""
        last_success = obj.login_attempts.filter(success=True).first()
        return last_success.timestamp if last_success else None


class TokenSerializer(serializers.Serializer):
    """Serializer for JWT token response"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = ProfileSerializer(read_only=True)
    
    @classmethod
    def get_token_for_user(cls, user):
        """Generate JWT tokens for user"""
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': ProfileSerializer(user).data
        }
        
