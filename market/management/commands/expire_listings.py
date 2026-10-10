from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from market import emails
from market.models import Listing, Mode

WARN_DAYS = 7  # sure dolmadan kac gun once hatirlatma e-postasi gider


class Command(BaseCommand):
    help = "Suresi dolan bireysel ikinci el ilanlari yayindan kaldirir (varsayilan 60 gun); dolmadan once ilan sahibine haber verir."

    def handle(self, *args, **options):
        days = getattr(settings, "LISTING_DAYS", 60)
        now = timezone.now()
        warn = Listing.objects.filter(mode=Mode.USED, is_active=True, pending_review=False, expiry_warned=False,
                                      created_at__lt=now - timedelta(days=days - WARN_DAYS),
                                      created_at__gte=now - timedelta(days=days))
        warned = 0
        for item in warn.select_related("owner"):
            if item.owner_id:
                emails.notify_listing_expiring(item, item.days_left)
                warned += 1
            Listing.objects.filter(pk=item.pk).update(expiry_warned=True)
        cutoff = now - timedelta(days=days)
        n = Listing.objects.filter(mode=Mode.USED, is_active=True, created_at__lt=cutoff).update(is_active=False)
        self.stdout.write(self.style.SUCCESS(f"{n} ilanin suresi doldu ({days} gun), {warned} hatirlatma gonderildi."))
