# -*- coding: utf-8 -*-
"""Yonetim paneli ana sayfasi: sekmeli, sade gorunum. Modelleri gruplar, Turkce ad ve aciklama verir."""
from django.contrib import admin
from django.urls import reverse

from django.utils.safestring import mark_safe

_P = {
    "list": "M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01",
    "flag": "M4 22V4m0 0h13l-2 4 2 4H4",
    "tag": "M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8zM7.5 7.5h.01",
    "star": "M12 3l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.8 6.1 21l1.2-6.5L2.5 9.9 9.1 9z",
    "search": "M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM21 21l-4.3-4.3",
    "store": "M3 9l1.5-5h15L21 9M3 9v11h18V9M3 9c0 1.7 1.3 3 3 3s3-1.3 3-3c0 1.7 1.3 3 3 3s3-1.3 3-3c0 1.7 1.3 3 3 3s3-1.3 3-3M9 20v-5h6v5",
    "mail": "M3 5h18v14H3zM3 6l9 7 9-7",
    "check": "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM8 12l3 3 5-6",
    "cart": "M3 4h2l2.4 11.5a2 2 0 0 0 2 1.5h7.7a2 2 0 0 0 2-1.5L21 8H6M9 21h.01M18 21h.01",
    "percent": "M19 5L5 19M7 9a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM17 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4z",
    "chat": "M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z",
    "user": "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21c1-4 4-6 8-6s7 2 8 6",
    "users": "M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM2 21c.8-4 3.5-6 7-6s6.2 2 7 6M17 3.5a4 4 0 0 1 0 7M22 21c-.4-2.6-1.7-4.4-3.5-5.2",
    "block": "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM5 5l14 14",
    "heart": "M12 21s-8-5.3-8-11a5 5 0 0 1 8-3.9A5 5 0 0 1 20 10c0 5.7-8 11-8 11z",
    "shield": "M12 22s8-3.5 8-10V5l-8-3-8 3v7c0 6.5 8 10 8 10z",
    "gear": "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z",
    "doc": "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M8 13h8M8 17h8",
    "image": "M3 5h18v14H3zM8.5 10a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zM21 16l-5-5-8 8",
    "globe": "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20",
    "pin": "M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12zM12 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z",
    "chart": "M3 3v18h18M7 15l4-4 3 3 5-6",
    "home": "M3 11l9-8 9 8M5 10v10h14V10",
    "dots": "M5 12h.01M12 12h.01M19 12h.01",
    "eye": "M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12zM12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z",
    "plus": "M12 5v14M5 12h14",
    "card": "M2 5h20v14H2zM2 10h20",
    "out": "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9",
}


def svg(key):
    d = _P.get(key, _P["dots"])
    return mark_safe('<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="%s"/></svg>' % d)


# object_name: (turkce ad, kisa aciklama, simge)
LABELS = {
    "Listing": ("İlanlar", "Tüm ilan ve ürünler", "list"),
    "ListingReport": ("İlan şikâyetleri", "Kullanıcı şikâyetleri", "flag"),
    "Category": ("Kategoriler", "Ana ve alt kategoriler", "tag"),
    "Boost": ("Öne çıkarmalar", "Ücretli/ücretsiz öne çıkan ilanlar", "star"),
    "SavedSearch": ("Kayıtlı aramalar", "Üyelerin kaydettiği aramalar", "search"),
    "Shop": ("Mağazalar", "Açık mağazalar", "store"),
    "ShopApplication": ("Mağaza başvuruları", "Onay bekleyen başvurular", "mail"),
    "VerificationRequest": ("Doğrulama başvuruları", "Mağaza doğrulama belgeleri", "check"),
    "Order": ("Siparişler", "Mağaza siparişleri", "cart"),
    "Coupon": ("Kuponlar", "İndirim kuponları", "percent"),
    "Review": ("Ürün yorumları", "Müşteri yorumları", "star"),
    "SellerReview": ("Satıcı değerlendirmeleri", "Satıcı puanları", "star"),
    "User": ("Üyeler", "Tüm kullanıcılar", "user"),
    "Group": ("Yetki grupları", "Personel grupları", "shield"),
    "UserBlock": ("Engellemeler", "Üyelerin engellediği kişiler", "block"),
    "Conversation": ("Konuşmalar", "Alıcı-satıcı mesajlaşmaları", "chat"),
    "Favorite": ("Favoriler", "Favoriye eklenen ilanlar", "heart"),
    "SiteSettings": ("Site ayarları", "Banner, SEO, Pixel, Analytics, şirket bilgisi", "gear"),
    "Banner": ("Reklam bannerları", "Ana sayfa ve liste bannerları", "image"),
    "Page": ("Sayfalar ve rehberler", "Hakkımızda, politikalar, rehber yazıları", "doc"),
    "Country": ("Ülkeler", "Ülke, para birimi ve kur", "globe"),
    "City": ("Şehirler", "Şehir listesi", "pin"),
    "DailyStat": ("Ziyaretçi istatistiği", "Günlük ziyaretçi sayıları", "chart"),
}

# sekme: (anahtar, baslik, simge, [model adlari])
TABS = [
    ("listings", "İlanlar", "list", ["Listing", "ListingReport", "Category", "Boost", "SavedSearch"]),
    ("shops", "Mağaza ve Sipariş", "store", ["Shop", "ShopApplication", "VerificationRequest", "Order", "Coupon", "Review", "SellerReview"]),
    ("people", "Üyeler", "users", ["User", "Conversation", "UserBlock", "Favorite", "Group"]),
    ("site", "Site ve İçerik", "gear", ["SiteSettings", "Page", "Banner", "Country", "City"]),
    ("stats", "İstatistik", "chart", ["DailyStat"]),
]


def _todo():
    from .models import ApplicationStatus, Listing, ListingReport, ShopApplication, VerificationRequest

    def link(name, qs=""):
        try:
            return reverse(name) + qs
        except Exception:
            return "#"
    items = [
        ("Onay bekleyen ilan", Listing.objects.filter(pending_review=True).count(),
         link("admin:market_listing_changelist", "?pending_review__exact=1")),
        ("Bekleyen mağaza başvurusu", ShopApplication.objects.filter(status=ApplicationStatus.PENDING).count(),
         link("admin:market_shopapplication_changelist")),
        ("Bekleyen doğrulama belgesi", VerificationRequest.objects.filter(status="pending").count(),
         link("admin:market_verificationrequest_changelist")),
        ("Çözülmemiş şikâyet", ListingReport.objects.filter(resolved=False).count(),
         link("admin:market_listingreport_changelist", "?resolved__exact=0")),
    ]
    return [{"label": a, "count": b, "url": c} for a, b, c in items]


def build_tabs(request):
    """Izinlere gore gorunen modelleri sekmelere dagitir. Haritada olmayan modeller 'Diger' sekmesine girer."""
    models = {}
    for app in admin.site.get_app_list(request):
        for m in app["models"]:
            models[m["object_name"]] = m

    registry = {mc._meta.object_name: mc for mc in admin.site._registry}

    def count(name):
        try:
            return registry[name]._default_manager.count()
        except Exception:
            return None

    def card(name):
        m = models.pop(name, None)
        if not m:
            return None
        label, desc, icon = LABELS.get(name, (m["name"], "", "•"))
        url = m.get("admin_url") or "#"
        if name == "SiteSettings":
            try:
                from .models import SiteSettings
                if SiteSettings.objects.exists():
                    url = reverse("admin:market_sitesettings_change", args=[1])
            except Exception:
                pass
        return {"label": label, "desc": desc, "icon": svg(icon), "url": url, "add": m.get("add_url"), "count": count(name)}

    todo = _todo()
    badge = {"listings": todo[0]["count"] + todo[3]["count"], "shops": todo[1]["count"] + todo[2]["count"]}
    tabs = []
    for key, title, icon, names in TABS:
        cards = [c for c in (card(n) for n in names) if c]
        if cards:
            tabs.append({"key": key, "title": title, "icon": svg(icon), "cards": cards, "badge": badge.get(key, 0)})
    rest = [card(n) for n in list(models)]
    rest = [c for c in rest if c]
    if rest:
        tabs.append({"key": "other", "title": "Diğer", "icon": svg("dots"), "cards": rest, "badge": 0})
    return tabs, todo
