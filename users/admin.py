from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import User, PasswordResetToken, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff', 'date_joined', 'failed_login_attempts', 'is_account_locked')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'is_email_verified', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Security Info', {
            'fields': ('is_email_verified', 'last_login_ip', 'failed_login_attempts', 'account_locked_until')
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'last_login_ip')
    
    def is_account_locked(self, obj):
        return obj.is_account_locked()
    is_account_locked.boolean = True
    is_account_locked.short_description = 'Account Locked'
    
    actions = ['unlock_accounts', 'lock_accounts']
    
    def unlock_accounts(self, request, queryset):
        count = 0
        for user in queryset:
            user.unlock_account()
            count += 1
        self.message_user(request, f'Successfully unlocked {count} accounts.')
    unlock_accounts.short_description = 'Unlock selected accounts'
    
    def lock_accounts(self, request, queryset):
        count = 0
        for user in queryset:
            user.lock_account()
            count += 1
        self.message_user(request, f'Successfully locked {count} accounts.')
    lock_accounts.short_description = 'Lock selected accounts'


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'used_at', 'is_valid_status')
    list_filter = ('created_at', 'expires_at', 'used_at')
    search_fields = ('user__email', 'user__username', 'token')
    readonly_fields = ('token', 'created_at', 'expires_at')
    ordering = ('-created_at',)
    
    def is_valid_status(self, obj):
        return obj.is_valid()
    is_valid_status.boolean = True
    is_valid_status.short_description = 'Valid'
    
    actions = ['mark_as_used', 'delete_expired']
    
    def mark_as_used(self, request, queryset):
        count = 0
        for token in queryset:
            if token.is_valid():
                token.mark_as_used()
                count += 1
        self.message_user(request, f'Successfully marked {count} tokens as used.')
    mark_as_used.short_description = 'Mark selected tokens as used'
    
    def delete_expired(self, request, queryset):
        expired_tokens = queryset.filter(expires_at__lt=timezone.now())
        count = expired_tokens.count()
        expired_tokens.delete()
        self.message_user(request, f'Successfully deleted {count} expired tokens.')
    delete_expired.short_description = 'Delete expired tokens'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('email', 'ip_address', 'success', 'timestamp', 'user_link')
    list_filter = ('success', 'timestamp')
    search_fields = ('email', 'ip_address', 'user__username')
    readonly_fields = ('email', 'ip_address', 'user_agent', 'success', 'timestamp', 'user')
    ordering = ('-timestamp',)
    
    def user_link(self, obj):
        if obj.user:
            return obj.user.username
        return 'Unknown'
    user_link.short_description = 'User'
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation
    
    def has_change_permission(self, request, obj=None):
        return False  # Don't allow editing
    
    actions = ['delete_old_attempts']
    
    def delete_old_attempts(self, request, queryset):
        old_date = timezone.now() - timezone.timedelta(days=90)
        old_attempts = queryset.filter(timestamp__lt=old_date)
        count = old_attempts.count()
        old_attempts.delete()
        self.message_user(request, f'Successfully deleted {count} old login attempts.')
    delete_old_attempts.short_description = 'Delete attempts older than 90 days'
