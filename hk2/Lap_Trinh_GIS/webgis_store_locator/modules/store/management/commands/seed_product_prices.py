from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand

from modules.store.models import SanPham


class Command(BaseCommand):
    help = "Seed default prices for products that do not have a selling price yet."

    def handle(self, *args, **options):
        updated = 0
        for idx, product in enumerate(SanPham.objects.order_by("pk"), start=1):
            if product.gia_ban and product.gia_ban > 0:
                continue
            product.gia_ban = Decimal(15000 + (idx % 12) * 5000)
            product.save(update_fields=["gia_ban"])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded prices for {updated} products."))
