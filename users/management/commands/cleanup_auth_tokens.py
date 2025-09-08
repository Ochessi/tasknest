from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from users.models import PasswordResetToken, LoginAttempt


class Command(BaseCommand):
    help = 'Clean up expired authentication tokens and old login attempts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete login attempts older than this many days (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting cleanup (dry_run={dry_run})...')
        )
        
        # Clean up expired password reset tokens
        expired_tokens = PasswordResetToken.objects.filter(
            expires_at__lt=timezone.now()
        )
        expired_count = expired_tokens.count()
        
        # Clean up old login attempts
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        old_attempts = LoginAttempt.objects.filter(
            timestamp__lt=cutoff_date
        )
        old_attempts_count = old_attempts.count()
        
        if dry_run:
            self.stdout.write(
                f'Would delete {expired_count} expired password reset tokens'
            )
            self.stdout.write(
                f'Would delete {old_attempts_count} login attempts older than {days} days'
            )
        else:
            with transaction.atomic():
                expired_tokens.delete()
                old_attempts.delete()
                
            self.stdout.write(
                self.style.SUCCESS(
                    f'Deleted {expired_count} expired password reset tokens'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Deleted {old_attempts_count} login attempts older than {days} days'
                )
            )
        
        self.stdout.write(self.style.SUCCESS('Cleanup completed!'))
