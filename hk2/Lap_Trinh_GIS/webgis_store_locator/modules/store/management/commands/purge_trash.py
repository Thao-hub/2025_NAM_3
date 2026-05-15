from django.core.management.base import BaseCommand
from django.utils import timezone

from modules.store.models import TrashRecord


class Command(BaseCommand):
    help = "Xóa vĩnh viễn các bản ghi thùng rác đã hết hạn."

    def handle(self, *args, **options):
        deleted_count, _ = TrashRecord.objects.filter(expires_at__lt=timezone.now()).delete()
        self.stdout.write(self.style.SUCCESS(f"Purged {deleted_count} expired trash record(s)."))
