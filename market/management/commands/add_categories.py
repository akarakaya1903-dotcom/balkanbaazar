# -*- coding: utf-8 -*-
"""Mevcut verilere dokunmadan kategori ekler. Tekrar calistirmak guvenlidir:
ayni slug varsa atlar, kayitlari silmez veya ezmez.

Kullanim:  python manage.py add_categories

Yeni kategori eklemek icin NEW_CATS listesine ayni bicimde bir satir ekle.
"""
from django.core.management.base import BaseCommand
from django.db.models import Max

from market.models import Category, Mode

# (mode, slug, ikon, adlar, [(alt_slug, adlar), ...])
NEW_CATS = [
    (Mode.SHOP, "turizm", "🧭",
     {"tr": "Turizm", "en": "Tourism", "mk": "Туризам", "sq": "Turizëm"},
     [
         ("turizm-turlar", {"tr": "Turlar ve tur paketleri", "en": "Tours and packages",
                            "mk": "Турови и пакети", "sq": "Turne dhe paketa"}),
         ("turizm-gunubirlik", {"tr": "Günübirlik geziler", "en": "Day trips",
                                "mk": "Дневни излети", "sq": "Shëtitje ditore"}),
         ("turizm-konaklama", {"tr": "Otel ve konaklama", "en": "Hotels and stays",
                               "mk": "Хотели и сместување", "sq": "Hotele dhe akomodim"}),
         ("turizm-transfer", {"tr": "Transfer ve ulaşım", "en": "Transfers and transport",
                              "mk": "Трансфери и превоз", "sq": "Transfere dhe transport"}),
         ("turizm-rehber", {"tr": "Rehberlik hizmetleri", "en": "Guide services",
                            "mk": "Услуги на водич", "sq": "Shërbime udhëzuesi"}),
         ("turizm-bilet", {"tr": "Uçak ve otobüs bileti", "en": "Flight and bus tickets",
                           "mk": "Авионски и автобуски билети", "sq": "Bileta avioni dhe autobusi"}),
         ("turizm-aktivite", {"tr": "Aktivite ve deneyimler", "en": "Activities and experiences",
                              "mk": "Активности и искуства", "sq": "Aktivitete dhe përvoja"}),
         ("turizm-vize", {"tr": "Vize ve seyahat danışmanlığı", "en": "Visa and travel consulting",
                          "mk": "Визи и патничко советување", "sq": "Vizë dhe këshillim udhëtimi"}),
     ]),
    (Mode.SHOP, "arac-kiralama", "🚗",
     {"tr": "Araç kiralama", "en": "Car rental", "mk": "Изнајмување возила", "sq": "Qira makinash"},
     [
         ("arac-kiralama-ekonomik", {"tr": "Ekonomik araçlar", "en": "Economy cars",
                                     "mk": "Економични возила", "sq": "Makina ekonomike"}),
         ("arac-kiralama-suv", {"tr": "SUV ve 4x4", "en": "SUV and 4x4",
                                "mk": "SUV и 4x4", "sq": "SUV dhe 4x4"}),
         ("arac-kiralama-van", {"tr": "Minibüs ve van", "en": "Vans and minibuses",
                                "mk": "Комбиња и минибуси", "sq": "Furgona dhe minibusë"}),
         ("arac-kiralama-luks", {"tr": "Lüks ve VIP", "en": "Luxury and VIP",
                                 "mk": "Луксузни и VIP", "sq": "Luksoze dhe VIP"}),
     ]),
]


class Command(BaseCommand):
    help = "Turizm ve arac kiralama kategorilerini (alt kategorileriyle) mevcut verilere dokunmadan ekler."

    def handle(self, *args, **options):
        for mode, slug, icon, names, subs in NEW_CATS:
            root = Category.objects.filter(mode=mode, parent=None, slug=slug).first()
            if root:
                self.stdout.write(f"var      : {slug}")
            else:
                last = Category.objects.filter(mode=mode, parent=None).aggregate(m=Max("order"))["m"]
                root = Category.objects.create(
                    mode=mode, parent=None, slug=slug, icon=icon, names=names,
                    order=(last if last is not None else -1) + 1,
                )
                self.stdout.write(self.style.SUCCESS(f"eklendi  : {slug}"))
            for k, (sub_slug, sub_names) in enumerate(subs):
                exists = Category.objects.filter(mode=mode, parent=root, slug=sub_slug).exists()
                if exists:
                    self.stdout.write(f"  var    : {sub_slug}")
                    continue
                Category.objects.create(
                    mode=mode, parent=root, slug=sub_slug, icon=icon, names=sub_names, order=k,
                )
                self.stdout.write(self.style.SUCCESS(f"  eklendi: {sub_slug}"))
