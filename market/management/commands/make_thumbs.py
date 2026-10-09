"""Mevcut ilan fotograflari icin kucuk onizlemeleri uretir. Tekrar calistirmak guvenlidir."""
from django.core.management.base import BaseCommand

from market.models import Listing, make_thumb


class Command(BaseCommand):
    help = "Liste kartlari icin kucuk onizleme fotograflari uretir"

    def handle(self, *args, **options):
        n = 0
        for item in Listing.objects.exclude(image="").exclude(image__isnull=True).iterator():
            import os
            tname = os.path.splitext(item.image.name)[0] + "_t.jpg"
            if item.image.storage.exists(tname):
                continue
            if make_thumb(item.image):
                n += 1
        self.stdout.write(f"onizleme: {n}")
