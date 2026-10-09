# -*- coding: utf-8 -*-
"""Yonetim paneli ana sayfasi: sekmeli, sade gorunum. Modelleri gruplar, Turkce ad ve aciklama verir."""
from django.contrib import admin
from django.urls import reverse

# object_name: (turkce ad, kisa aciklama, simge)
LABELS = {
    "Listing": ("İlanlar", "Tüm ilan ve ürünler", "▦"),
    "ListingReport": ("İlan şikâyetleri", "Kullanıcı şikâyetleri", "⚑"),
    "Category": ("Kategoriler", "Ana ve alt kategoriler", "☰"),
    "Boost": ("Öne çıkarmalar", "Ücretli/ücretsiz öne çıkan ilanlar", "★"),
    "SavedSearch": ("Kayıtlı aramalar", "Üyelerin kaydettiği aramalar", "⌕"),
    "Shop": ("Mağazalar", "Açık mağazalar", "◧"),
    "ShopApplication": ("Mağaza başvuruları", "Onay bekleyen başvurular", "✉"),
    "VerificationRequest": ("Doğrulama başvuruları", "Mağaza doğrulama belgeleri", "✔"),
    "Order": ("Siparişler", "Mağaza siparişleri", "🛒"),
    "Coupon": ("Kuponlar", "İndirim kuponları", "%"),
    "Review": ("Ürün yorumları", "Müşteri yorumları", "✎"),
    "SellerReview": ("Satıcı değerlendirmeleri", "Satıcı puanları", "☆"),
    "User": ("Üyeler", "Tüm kullanıcılar", "☺"),
    "Group": ("Yetki grupları", "Personel grupları", "⚿"),
    "UserBlock": ("Engellemeler", "Üyelerin engellediği kişiler", "⛔"),
    "Conversation": ("Konuşmalar", "Alıcı-satıcı mesajlaşmaları", "✉"),
    "Favorite": ("Favoriler", "Favoriye eklenen ilanlar", "♥"),
    "SiteSettings": ("Site ayarları", "Banner, SEO, Pixel, Analytics, şirket bilgisi", "⚙"),
    "Banner": ("Reklam bannerları", "Ana sayfa ve liste bannerları", "▭"),
    "Page": ("Sayfalar ve rehberler", "Hakkımızda, politikalar, rehber yazıları", "☷"),
    "Country": ("Ülkeler", "Ülke, para birimi ve kur", "◍"),
    "City": ("Şehirler", "Şehir listesi", "⌂"),
    "DailyStat": ("Ziyaretçi istatistiği", "Günlük ziyaretçi sayıları", "▤"),
}

# sekme: (anahtar, baslik, simge, [model adlari])
TABS = [
    ("listings", "İlanlar", "▦", ["Listing", "ListingReport", "Category", "Boost", "SavedSearch"]),
    ("shops", "Mağaza ve Sipariş", "◧", ["Shop", "ShopApplication", "VerificationRequest", "Order", "Coupon", "Review", "SellerReview"]),
    ("people", "Üyeler", "☺", ["User", "Conversation", "UserBlock", "Favorite", "Group"]),
    ("site", "Site ve İçerik", "⚙", ["SiteSettings", "Page", "Banner", "Country", "City"]),
    ("stats", "İstatistik", "▤", ["DailyStat"]),
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
        return {"label": label, "desc": desc, "icon": icon, "url": url, "add": m.get("add_url")}

    todo = _todo()
    badge = {"listings": todo[0]["count"] + todo[3]["count"], "shops": todo[1]["count"] + todo[2]["count"]}
    tabs = []
    for key, title, icon, names in TABS:
        cards = [c for c in (card(n) for n in names) if c]
        if cards:
            tabs.append({"key": key, "title": title, "icon": icon, "cards": cards, "badge": badge.get(key, 0)})
    rest = [card(n) for n in list(models)]
    rest = [c for c in rest if c]
    if rest:
        tabs.append({"key": "other", "title": "Diğer", "icon": "…", "cards": rest, "badge": 0})
    return tabs, todo
