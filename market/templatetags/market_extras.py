from django import template
from django.db.models import Q
from django.utils import timezone
from django.utils.http import urlencode

from market.models import Banner, Page

register = template.Library()


@register.simple_tag
def price(listing, country):
    """Ilan fiyatini secili ulkenin para biriminde yazar."""
    if country is None:
        return f"€ {listing.price_eur:,.0f}".replace(",", ".")
    return country.format_price(listing.price_eur)


@register.simple_tag
def eur(listing):
    return f"€ {listing.price_eur:,.0f}".replace(",", ".")


@register.simple_tag(takes_context=True)
def qs(context, **kwargs):
    """Mevcut GET parametrelerini koruyarak link uretir."""
    params = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value in (None, "", "None"):
            params.pop(key, None)
        else:
            params[key] = value
    params.pop("page", None) if "page" not in kwargs else None
    return "?" + urlencode(params) if params else ""


@register.simple_tag
def catname(category, lang):
    return category.name(lang)


@register.filter
def tile(hue):
    return (
        f"background:linear-gradient(145deg,hsl({hue} 46% 92%),hsl({(hue + 26) % 360} 42% 80%))"
    )


@register.simple_tag
def countryname(country, lang):
    """Ulke adini secili dile gore yazar."""
    return country.display_name(lang) if country else ""


@register.simple_tag
def banners(place):
    """Su an yayinda olan banner'lar (tarih araligi ve 'yayinda' isaretine gore)."""
    now = timezone.now()
    try:
        return list(Banner.objects.filter(is_active=True, place=place)
                    .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=now))
                    .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=now))[:8])
    except Exception:  # migrate calistirilmadiysa site yine acilsin
        return []


@register.simple_tag
def footer_pages(group):
    try:
        return list(Page.objects.filter(group=group, is_published=True))
    except Exception:
        return []
