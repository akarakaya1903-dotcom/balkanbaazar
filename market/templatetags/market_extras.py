from django import template
from django.db.models import Q
from django.utils import timezone
from django.utils.http import urlencode

from django.utils.safestring import mark_safe

from market import antispam
from market.models import Banner, Page

register = template.Library()


@register.simple_tag
def price(listing, country):
    """Ilan fiyatini secili ulkenin para biriminde yazar."""
    if listing.price_input is not None and listing.price_currency:
        return listing.display_price(country)
    if country is None:
        return f"€ {listing.price_eur:,.0f}".replace(",", ".")
    return country.format_price(listing.price_eur)


@register.simple_tag
def price_alt(listing):
    """Girilen para biriminden farkli yaklasik karsilik (yoksa bos)."""
    return listing.alt_price()


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


@register.simple_tag
def footer_seo(country, lang):
    """Alt bilgi icin tarayici dostu ic baglantilar: ana kategoriler + 'kategori sehir' birlesimleri."""
    from django.core.cache import cache
    from market.models import City, Category, Mode
    code = getattr(country, "code", "") or ""
    key = f"footer_seo:{code}:{lang}"
    data = cache.get(key)
    if data is not None:
        return data
    cats, combos = [], []
    try:
        roots = list(Category.objects.filter(mode=Mode.USED, parent__isnull=True)[:10])
        for r in roots:
            cats.append({"name": r.name(lang), "url": seo_url(Mode.USED, r.slug)})
        cities = list(City.objects.filter(country=country)[:3]) if country else []
        for city in cities:
            for r in roots[:3]:
                combos.append({"name": f"{r.name(lang)} · {city.name}",
                               "url": seo_url(Mode.USED, r.slug, city=city.name)})
    except Exception:
        cats, combos = [], []
    data = {"cats": cats, "combos": combos}
    cache.set(key, data, 600)
    return data


@register.filter
def digits(value):
    """Telefondaki rakam disi karakterleri atar (wa.me baglantisi icin)."""
    return "".join(ch for ch in str(value or "") if ch.isdigit())


@register.simple_tag
def antispam_fields():
    return mark_safe(
        '<input type="text" name="website" tabindex="-1" autocomplete="off" '
        'style="position:absolute;left:-9999px;opacity:0;height:0;width:0" aria-hidden="true">'
        f'<input type="hidden" name="bbts" value="{antispam.make_token()}">'
    )


@register.simple_tag(takes_context=True)
def listing_jsonld(context, item):
    """Ilan sayfasi icin Google'in anladigi Product verisi."""
    import json
    request = context["request"]
    in_stock = item.is_active and not (item.track_stock and (item.stock or 0) <= 0)
    url = request.build_absolute_uri(request.path)
    data = {
        "@context": "https://schema.org", "@type": "Product",
        "name": item.title, "description": (item.description or item.title)[:500], "url": url,
        "itemCondition": "https://schema.org/NewCondition" if item.condition == "new" else "https://schema.org/UsedCondition",
        "offers": {"@type": "Offer", "price": str(item.price_eur), "priceCurrency": "EUR", "url": url,
                   "availability": "https://schema.org/InStock" if in_stock else "https://schema.org/OutOfStock"},
    }
    if item.image:
        data["image"] = [request.build_absolute_uri(item.image.url)]
    scripts = [data]
    # Gezinti yolu (Ana sayfa > Kategori > Alt kategori > Ilan): aramada ilan adresinin ustunde yol gorunur
    try:
        lang = context.get("lang") or "en"
        root = item.category.parent or item.category
        crumbs = [("Balkan Baazar", request.build_absolute_uri("/" + lang + "/"))]
        crumbs.append((root.name(lang), request.build_absolute_uri(seo_url(item.mode, root.slug))))
        if item.category.parent:
            crumbs.append((item.category.name(lang), request.build_absolute_uri(seo_url(item.mode, root.slug, item.category.slug))))
        crumbs.append((item.title, url))
        scripts.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                        "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                                            for i, (n, u) in enumerate(crumbs)]})
    except Exception:
        pass
    return mark_safe("".join('<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False).replace("</", "<\\/") + "</script>" for d in scripts))


@register.filter
def ptitle(page, lang):
    return page.localized(lang)[0]


@register.simple_tag
def seo_url(mode, cat, sub=None, city=None):
    """Temiz adresli kategori/sehir sayfasi baglantisi."""
    from django.urls import reverse
    from django.utils.text import slugify
    if city:
        c = slugify(city)
        return reverse("market:seo_city_sub", args=[c, mode, cat, sub]) if sub else reverse("market:seo_city", args=[c, mode, cat])
    return reverse("market:seo_sub", args=[mode, cat, sub]) if sub else reverse("market:seo_category", args=[mode, cat])


@register.simple_tag
def attr_rows(item, lang):
    from market import attributes
    return attributes.display_rows(item, lang)


@register.simple_tag
def user_verified(user):
    from market.models import email_is_verified
    return bool(user and email_is_verified(user))


@register.simple_tag
def seller_rating_of(user):
    from market.models import seller_rating
    return seller_rating(user) if user else (None, 0)


@register.simple_tag
def cat_icon(c, size=""):
    """Kategori icin pastel zeminli cizgi simge (ya da yuklenmis fotograf)."""
    from market import icons
    if getattr(c, "image", None):
        return mark_safe(f'<span class="ic cat-ic photo {size}" style="background-image:url({c.image.url})"></span>')
    key = icons.SLUG_ICON.get(c.slug, "tag")
    bg, fg = icons.TONES[key]
    return mark_safe(
        f'<span class="ic cat-ic {size}" style="background:{bg};color:{fg}">'
        f'<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{icons.ICONS[key]}</svg></span>')


@register.filter
def thumb(fieldfile):
    """Kucuk onizleme varsa onun adresini, yoksa orijinali dondurur."""
    try:
        import os
        base, _ext = os.path.splitext(fieldfile.name)
        tname = base + "_t.jpg"
        if fieldfile.storage.exists(tname):
            return fieldfile.storage.url(tname)
    except Exception:
        pass
    return fieldfile.url


@register.simple_tag
def faq_bot(lang):
    """Yardim botu icin JSON verisi (soru/cevap + arayuz metinleri + link adresleri)."""
    from django.urls import reverse

    from market.faq_bot import LINK_SLUGS, bot_data
    ui, qa = bot_data(lang)
    links = {k: reverse("market:page", args=[slug]) for k, slug in LINK_SLUGS.items()}
    links["post"] = reverse("market:my_listing_new")
    links["shops"] = reverse("market:shop_apply")
    links["contact"] = reverse("market:page", args=["iletisim"])
    return {"ui": ui, "qa": qa, "links": links}


_ASSET_V = {}


@register.simple_tag
def asset(path):
    """static adresi + dosya degisince degisen ?v= (tarayici eski CSS'i onbellekte tutmasin)."""
    import os

    from django.conf import settings
    from django.contrib.staticfiles import finders
    from django.templatetags.static import static
    if path not in _ASSET_V:
        v = ""
        try:
            f = os.path.join(str(settings.STATIC_ROOT), path) if getattr(settings, "STATIC_ROOT", None) else ""
            if not (f and os.path.exists(f)):
                f = finders.find(path) or ""
            if f:
                v = str(int(os.path.getmtime(f)))
        except Exception:
            v = ""
        _ASSET_V[path] = v
    url = static(path)
    return url + ("?v=" + _ASSET_V[path] if _ASSET_V[path] else "")
