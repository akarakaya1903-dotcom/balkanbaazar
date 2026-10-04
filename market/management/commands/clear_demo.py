from django.core.management.base import BaseCommand

from market.models import Listing, Shop


class Command(BaseCommand):
    help = "Sahibi olmayan demo ilan ve magazalari siler (gercek kullanici verisine dokunmaz)."

    def handle(self, *args, **options):
        l = Listing.objects.filter(owner__isnull=True).delete()
        s = Shop.objects.filter(owner__isnull=True).delete()
        self.stdout.write(self.style.SUCCESS(f"Silinen ilanlar: {l[0]}, magazalar: {s[0]}"))
