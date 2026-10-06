from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Avg

from market.models import Listing, Review, Shop


class Command(BaseCommand):
    help = "Puanlari gercek yorumlara gore yeniden hesaplar; yorumu olmayanlari 0 (=Yeni) yapar. Tekrar calistirmak guvenli."

    def handle(self, *args, **options):
        for item in Listing.objects.all():
            avg = Review.objects.filter(listing=item).aggregate(a=Avg("rating"))["a"]
            Listing.objects.filter(pk=item.pk).update(rating=Decimal(str(round(avg, 1))) if avg else 0)
        for shop in Shop.objects.all():
            avg = Review.objects.filter(listing__shop=shop).aggregate(a=Avg("rating"))["a"]
            Shop.objects.filter(pk=shop.pk).update(rating=Decimal(str(round(avg, 1))) if avg else 0)
        self.stdout.write(self.style.SUCCESS("Puanlar guncellendi."))
