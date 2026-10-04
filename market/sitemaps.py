from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Listing, Page, Shop


class StaticSitemap(Sitemap):
    protocol = "https"
    priority = 0.8

    def items(self):
        return ["market:home", "market:listings", "market:shops", "market:trending", "market:pricing"]

    def location(self, name):
        return reverse(name)


class ListingSitemap(Sitemap):
    protocol = "https"
    priority = 0.6
    limit = 5000

    def items(self):
        return Listing.objects.filter(is_active=True).order_by("-id")[:20000]

    def location(self, obj):
        return reverse("market:listing_detail", args=[obj.pk, obj.slug])


class ShopSitemap(Sitemap):
    protocol = "https"
    priority = 0.7

    def items(self):
        return Shop.objects.all()

    def location(self, obj):
        return reverse("market:shop_detail", args=[obj.slug])


class PageSitemap(Sitemap):
    protocol = "https"
    priority = 0.4

    def items(self):
        return Page.objects.filter(is_published=True)

    def location(self, obj):
        return reverse("market:page", args=[obj.slug])
