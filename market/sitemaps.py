from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from django.utils.text import slugify

from .models import Category, Listing, Page, Shop


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


class CategorySitemap(Sitemap):
    """Kategori ve kategori+sehir sayfalari (yalnizca aktif ilani olanlar)."""
    protocol = "https"
    priority = 0.7

    def items(self):
        seen = set()
        for mode, cslug, pslug, city in (Listing.objects.filter(is_active=True)
                                         .values_list("mode", "category__slug", "category__parent__slug", "city__name")
                                         .distinct()):
            root, sub = (pslug, cslug) if pslug else (cslug, None)
            seen.add((mode, root, None, None))
            if sub:
                seen.add((mode, root, sub, None))
            if city:
                seen.add((mode, root, None, slugify(city)))
                if sub:
                    seen.add((mode, root, sub, slugify(city)))
        return sorted(seen, key=lambda x: tuple(str(i) for i in x))

    def location(self, obj):
        from django.urls import reverse
        mode, root, sub, city = obj
        if city:
            return reverse("market:seo_city_sub", args=[city, mode, root, sub]) if sub else reverse("market:seo_city", args=[city, mode, root])
        return reverse("market:seo_sub", args=[mode, root, sub]) if sub else reverse("market:seo_category", args=[mode, root])


SITEMAP_LANGS = ["tr", "en", "mk", "sq", "sr", "bs", "hr", "bg", "el"]


def expand(base):
    """Her adresi dil onekli olarak da (her dil icin ayri) listeler."""
    class Expanded(base):
        def items(self):
            return [(obj, lang) for obj in base.items(self) for lang in SITEMAP_LANGS]

        def location(self, pair):
            obj, lang = pair
            return f"/{lang}{base.location(self, obj)}"
    Expanded.__name__ = base.__name__
    return Expanded
