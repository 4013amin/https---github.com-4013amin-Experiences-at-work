from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app.models import OTP


class Command(BaseCommand):
    help = 'پاک کردن کدهای OTP منقضی شده از دیتابیس'

    def handle(self, *args, **kwargs):
        threshold = timezone.now() - timedelta(minutes=10)
        deleted_count, _ = OTP.objects.filter(created_at__lt=threshold).delete()

        self.stdout.write(self.style.SUCCESS(f'تعداد {deleted_count} کد منقضی شده پاک شد.'))