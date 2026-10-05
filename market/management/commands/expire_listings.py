from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from market.models import Listing, Mode


class Command(BaseCommand):
    help = "Suresi dolan bireysel ikinci el ilanlari yayindan kaldirir (varsayilan 60 gun)."

    def handle(self, *args, **options):
        days = getattr(settings, "LISTING_DAYS", 60)
        cutoff = timezone.now() - timedelta(days=days)
        n = Listing.objects.filter(mode=Mode.USED, is_active=True, created_at__lt=cutoff).update(is_active=False)
        self.stdout.write(self.style.SUCCESS(f"{n} ilanin suresi doldu ({days} gun)."))
