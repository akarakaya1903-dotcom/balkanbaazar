# -*- coding: utf-8 -*-
"""Ornek veri: 8 ulke, sehirler, kategoriler, magazalar, ilanlar.

Kullanim:  python manage.py seed --reset
"""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from market.models import Category, City, Country, Listing, Mode, Shop, ShopPlan

COUNTRIES = [
    # code, local, tr, en, flag, lang, currency, symbol, rate/EUR, cities
    ("MK", "Severna Makedonija", "Kuzey Makedonya", "North Macedonia", "🇲🇰", "mk", "MKD", "ден", 61.5,
     ["Skopje", "Bitola", "Kumanovo", "Tetovo", "Ohrid", "Gostivar", "Štip", "Struga"]),
    ("AL", "Shqipëri", "Arnavutluk", "Albania", "🇦🇱", "sq", "ALL", "L", 100.5,
     ["Tiranë", "Durrës", "Vlorë", "Shkodër", "Elbasan", "Fier", "Korçë"]),
    ("XK", "Kosovë", "Kosova", "Kosovo", "🇽🇰", "sq", "EUR", "€", 1,
     ["Prishtinë", "Prizren", "Pejë", "Gjakovë", "Mitrovicë", "Ferizaj", "Gjilan"]),
    ("RS", "Srbija", "Sırbistan", "Serbia", "🇷🇸", "sr", "RSD", "дин", 117.2,
     ["Beograd", "Novi Sad", "Niš", "Kragujevac", "Subotica", "Novi Pazar", "Čačak"]),
    ("ME", "Crna Gora", "Karadağ", "Montenegro", "🇲🇪", "cnr", "EUR", "€", 1,
     ["Podgorica", "Nikšić", "Budva", "Bar", "Herceg Novi", "Kotor", "Bijelo Polje"]),
    ("BA", "Bosna i Hercegovina", "Bosna-Hersek", "Bosnia and Herzegovina", "🇧🇦", "bs", "BAM", "KM", 1.9558,
     ["Sarajevo", "Banja Luka", "Tuzla", "Zenica", "Mostar", "Bihać", "Brčko"]),
    ("BG", "България", "Bulgaristan", "Bulgaria", "🇧🇬", "bg", "EUR", "€", 1,
     ["София", "Пловдив", "Варна", "Бургас", "Русе", "Стара Загора", "Благоевград"]),
    ("GR", "Ελλάδα", "Yunanistan", "Greece", "🇬🇷", "el", "EUR", "€", 1,
     ["Αθήνα", "Θεσσαλονίκη", "Πάτρα", "Λάρισα", "Ηράκλειο", "Καβάλα", "Ιωάννινα"]),
]


def names(tr, en, mk, sq, sr, bg, el):
    return {"tr": tr, "en": en, "mk": mk, "sq": sq, "sr": sr,
            "bs": sr, "hr": sr, "cnr": sr, "bg": bg, "el": el}


USED_CATS = [
    ("vasita", "🚗", names("Vasıta", "Vehicles", "Возила", "Automjete", "Возила", "Превозни средства", "Οχήματα"),
     ["Otomobil", "Arazi/SUV", "Motosiklet", "Ticari araç", "Yedek parça", "Lastik & jant"],
     ["Golf 7 1.6 TDI", "Astra 1.4 T", "Clio IV", "Passat B8", "Yaris Hybrid", "Transporter T6", "Octavia Combi", "Punto Evo"],
     (2500, 28000)),
    ("emlak", "🏠", names("Emlak", "Real estate", "Недвижнини", "Patundshmëri", "Некретнине", "Имоти", "Ακίνητα"),
     ["Satılık daire", "Kiralık daire", "Müstakil ev", "Arsa", "İş yeri", "Devremülk"],
     ["2+1 daire, merkez", "3+1 bahçeli", "Stüdyo, üniversiteye yakın", "Arsa 480 m²", "Dükkân, cadde üzeri", "Yazlık, deniz manzaralı", "Villa 4+2", "Depo 300 m²"],
     (28000, 290000)),
    ("elektronik", "📱", names("Elektronik", "Electronics", "Електроника", "Elektronikë", "Електроника", "Електроника", "Ηλεκτρονικά"),
     ["Telefon", "Bilgisayar", "Televizyon", "Fotoğraf & kamera", "Oyun konsolu", "Ses sistemi"],
     ["iPhone 13 128 GB", "Galaxy S23", "MacBook Air M2", "Lenovo ThinkPad", "LG OLED 55\"", "PlayStation 5", "Canon EOS 250D", "JBL Charge 5"],
     (40, 1400)),
    ("ev-yasam", "🛋️", names("Ev & Yaşam", "Home & living", "Дом и живеење", "Shtëpi", "Кућа", "Дом", "Σπίτι"),
     ["Mobilya", "Beyaz eşya", "Bahçe", "Mutfak", "Aydınlatma", "Dekorasyon"],
     ["3 kişilik kanepe", "Yemek masası + 6 sandalye", "Buzdolabı No-Frost", "Çamaşır makinesi 9 kg", "Gardırop 4 kapılı", "Halı 160x230", "Bahçe seti", "Kitaplık"],
     (25, 900)),
    ("giyim", "👕", names("Giyim", "Fashion", "Облека", "Veshje", "Одећа", "Облекло", "Ρούχα"),
     ["Kadın giyim", "Erkek giyim", "Ayakkabı", "Çanta", "Saat", "Takı"],
     ["Deri ceket", "Kışlık mont", "Spor ayakkabı 42", "Kol saati", "Omuz çantası", "Elbise M beden", "Kot pantolon", "Gümüş kolye"],
     (8, 320)),
    ("anne-bebek", "🧸", names("Anne & Bebek", "Baby & kids", "Мајка и бебе", "Nënë e fëmijë", "Мама и беба", "Майка и бебе", "Μαμά & μωρό"),
     ["Bebek arabası", "Oto koltuğu", "Oyuncak", "Bebek giyim", "Beşik", "Mama sandalyesi"],
     ["Bebek arabası travel sistem", "Oto koltuğu 0–18 kg", "Ahşap beşik", "Mama sandalyesi", "Oyun halısı", "Bebek küveti", "Kanguru", "Oyuncak seti"],
     (12, 420)),
    ("hobi-spor", "🎸", names("Hobi & Spor", "Hobby & sport", "Хоби и спорт", "Hobi e sport", "Хоби и спорт", "Хоби и спорт", "Χόμπι & αθλητισμός"),
     ["Müzik aleti", "Bisiklet", "Kamp", "Kitap", "Koleksiyon", "Fitness"],
     ["Akustik gitar", "Dağ bisikleti 29\"", "Çadır 4 kişilik", "Koşu bandı", "Kamp ocağı", "Roman seti", "Pul koleksiyonu", "Dambıl seti 20 kg"],
     (10, 700)),
    ("is-sanayi", "🧰", names("İş & Sanayi", "Business & industry", "Бизнис", "Biznes", "Бизнис", "Бизнес", "Επιχείρηση"),
     ["İş makinesi", "Tarım", "İnşaat", "Ofis", "Hırdavat", "Restoran ekipmanı"],
     ["Forklift 2.5 t", "Kompresör 100 L", "Kaynak makinesi", "Ofis masası seti", "Vitrin dolabı", "Sanayi fırını", "Jeneratör 5 kVA", "İskele seti"],
     (120, 9000)),
    ("is-ilanlari", "💼", names("İş İlanları", "Jobs", "Огласи за работа", "Punë", "Послови", "Работа", "Εργασία"),
     ["Tam zamanlı", "Yarı zamanlı", "Uzaktan", "Sezonluk", "Staj", "Freelance"],
     ["Satış danışmanı", "Garson", "Yazılım geliştirici", "Şoför C sınıfı", "Muhasebe elemanı", "Depo görevlisi", "Kuaför", "Çağrı merkezi"],
     (400, 2200)),
    ("hayvanlar", "🐕", names("Hayvanlar", "Pets", "Миленици", "Kafshë", "Кућни љубимци", "Домашни любимци", "Κατοικίδια"),
     ["Köpek", "Kedi", "Kuş", "Akvaryum", "Çiftlik hayvanı", "Aksesuar"],
     ["Golden Retriever yavru", "British Shorthair", "Muhabbet kuşu", "Akvaryum 120 L", "Kuş kafesi", "Köpek kulübesi", "Tasma seti", "Kedi tırmalama"],
     (15, 800)),
]

SHOP_CATS = [
    ("moda", "👗", names("Moda", "Fashion", "Мода", "Modë", "Мода", "Мода", "Μόδα"),
     ["Kadın", "Erkek", "Çocuk", "Ayakkabı", "Çanta", "Aksesuar"],
     ["Oversize sweatshirt", "Bisiklet yaka triko", "Deri bot", "Keten gömlek", "Crossbody çanta", "Slim fit pantolon", "Trençkot", "Şal"],
     (9, 260)),
    ("elektronik", "💻", names("Elektronik", "Electronics", "Електроника", "Elektronikë", "Електроника", "Електроника", "Ηλεκτρονικά"),
     ["Telefon", "Laptop", "Tablet", "Kulaklık", "Akıllı saat", "Aksesuar"],
     ["Kablosuz kulaklık ANC", "Akıllı saat GPS", "Bluetooth hoparlör", "Taşınabilir SSD 1 TB", "Powerbank 20000 mAh", "Mekanik klavye", "Webcam 1080p", "Tablet 11\""],
     (15, 1500)),
    ("ev-mobilya", "🏡", names("Ev & Mobilya", "Home & furniture", "Дом и мебел", "Shtëpi e mobilje", "Кућа и намештај", "Дом и мебели", "Σπίτι & έπιπλα"),
     ["Mobilya", "Tekstil", "Mutfak", "Banyo", "Aydınlatma", "Depolama"],
     ["Nordic yemek masası", "Köşe koltuk", "Kadife perde", "Seramik tabak seti", "Sarkıt lamba", "Yatak örtüsü", "Çekmeceli dolap", "Duvar rafı"],
     (12, 1200)),
    ("kozmetik", "💄", names("Kozmetik", "Beauty", "Козметика", "Kozmetikë", "Козметика", "Козметика", "Καλλυντικά"),
     ["Makyaj", "Cilt bakımı", "Parfüm", "Saç bakımı", "Erkek bakım", "Set & kutu"],
     ["Vitamin C serum", "Mat ruj seti", "Parfüm 50 ml", "Saç maskesi", "Güneş kremi SPF50", "Göz kalemi", "Yüz temizleme jeli", "Tıraş seti"],
     (5, 120)),
    ("market", "🛒", names("Market", "Supermarket", "Маркет", "Market", "Маркет", "Магазин", "Σούπερ μάρκετ"),
     ["Temel gıda", "İçecek", "Atıştırmalık", "Temizlik", "Kahve & çay", "Yerel lezzet"],
     ["Zeytinyağı 1 L", "Balkan kahvesi 500 g", "Ajvar 700 g", "Bal 950 g", "Organik makarna", "Kuruyemiş karışık", "Bitki çayı", "Reçel seti"],
     (2, 60)),
    ("spor", "⚽", names("Spor & Outdoor", "Sport & outdoor", "Спорт", "Sport", "Спорт", "Спорт", "Αθλητικά"),
     ["Spor giyim", "Ayakkabı", "Fitness", "Kamp", "Bisiklet", "Kayak"],
     ["Koşu ayakkabısı", "Yoga matı", "Dambıl 2x5 kg", "Termal tayt", "Uyku tulumu", "Kamp sandalyesi", "Bisiklet kaskı", "Şişme SUP board"],
     (8, 450)),
    ("anne-bebek", "🍼", names("Anne & Bebek", "Mother & baby", "Мајка и бебе", "Nënë e fëmijë", "Мама и беба", "Майка и бебе", "Μαμά & μωρό"),
     ["Bebek bezi", "Mama", "Bebek arabası", "Oyuncak", "Bebek giyim", "Güvenlik"],
     ["Bebek bezi 4 numara", "Islak mendil 12'li", "Biberon seti", "Katlanır bebek arabası", "Oyun parkı", "Bebek monitörü", "Tulum 6–9 ay", "Emzik seti"],
     (4, 300)),
    ("oto-yapi", "🔧", names("Oto & Yapı", "Auto & DIY", "Автоделови", "Auto e ndërtim", "Ауто и градња", "Авто и ремонт", "Αυτοκίνητο & DIY"),
     ["Oto aksesuar", "Yedek parça", "El aleti", "Boya", "Bahçe", "Elektrik"],
     ["Telefon tutucu", "Akü 60 Ah", "Matkap seti 18V", "Silecek takımı", "Oto kokusu", "Bahçe hortumu 20 m", "LED ampul seti", "Avuç taşlama"],
     (5, 400)),
    ("kitap-hobi", "📚", names("Kitap & Hobi", "Books & hobby", "Книги и хоби", "Libra e hobi", "Књиге и хоби", "Книги и хоби", "Βιβλία & χόμπι"),
     ["Kitap", "Kırtasiye", "Müzik", "Oyun", "Sanat malzemesi", "Puzzle"],
     ["Balkan mutfağı kitabı", "Not defteri seti", "Strateji oyunu", "Suluboya seti", "1000 parça puzzle", "Çocuk hikâye seti", "Gitar teli", "Dolma kalem"],
     (3, 90)),
    ("evcil-hayvan", "🐾", names("Evcil Hayvan", "Pet shop", "Миленици", "Kafshë", "Љубимци", "Любимци", "Κατοικίδια"),
     ["Köpek maması", "Kedi maması", "Kum & hijyen", "Oyuncak", "Tasma", "Kafes & kulübe"],
     ["Köpek maması 15 kg", "Kedi kumu 10 L", "Tahılsız kedi maması", "Ortopedik yatak", "Otomatik suluk", "Oyuncak fare seti", "Boyun tasması", "Taşıma çantası"],
     (4, 150)),
]

SHOP_WORDS = ["Vardar", "Ilinden", "Adriatik", "Pelister", "Skopje", "Balkan", "Drim", "Ohrid",
              "Kale", "Mavrovo", "Nova", "Bazar", "Sirok", "Dunav", "Morava", "Neretva"]
SHOP_SUFFIX = ["Store", "Market", "Shop", "Trade", "Home", "Tech", "Moda", "Center"]
SELLERS = ["Ana", "Marko", "Elif", "Dritan", "Nikola", "Ivana", "Mehmet", "Petar", "Jelena", "Arben"]
ADJ = ["Temiz", "Az kullanılmış", "Garantili", "Sahibinden", "Bakımlı", "Orijinal kutulu", "Acil", "Takaslı"]
HUES = [188, 200, 212, 168, 150, 226, 38, 260]


class Command(BaseCommand):
    help = "Balkan Baazar icin ornek veri olusturur."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Once tum veriyi siler")
        parser.add_argument("--per-sub", type=int, default=4, help="Alt kategori basina ilan")

    def handle(self, *args, **opts):
        random.seed(20)
        if opts["reset"]:
            Listing.objects.all().delete()
            Shop.objects.all().delete()
            Category.objects.all().delete()
            City.objects.all().delete()
            Country.objects.all().delete()
            self.stdout.write("Eski veri silindi.")

        # --- ulkeler ve sehirler ---
        countries = []
        for i, (code, local, tr, en, flag, lang, cur, sym, rate, cities) in enumerate(COUNTRIES):
            c, _ = Country.objects.update_or_create(
                code=code,
                defaults=dict(name_local=local, name_tr=tr, name_en=en, flag=flag, lang=lang,
                              currency=cur, symbol=sym, rate_per_eur=rate, order=i, is_active=True),
            )
            for j, city in enumerate(cities):
                City.objects.get_or_create(country=c, name=city, defaults={"order": j})
            countries.append(c)

        # --- kategoriler ---
        cat_map = {Mode.USED: [], Mode.SHOP: []}
        for mode, table in ((Mode.USED, USED_CATS), (Mode.SHOP, SHOP_CATS)):
            for order, (slug, icon, nm, subs, pool, price_range) in enumerate(table):
                root, _ = Category.objects.update_or_create(
                    mode=mode, parent=None, slug=slug,
                    defaults={"icon": icon, "names": nm, "order": order},
                )
                children = []
                for k, sub in enumerate(subs):
                    child, _ = Category.objects.update_or_create(
                        mode=mode, parent=root, slug=f"{slug}-{k + 1}",
                        defaults={"icon": icon, "names": {"tr": sub, "en": sub}, "order": k},
                    )
                    children.append(child)
                cat_map[mode].append((root, children, pool, price_range))

        # --- magazalar ---
        now = timezone.now()
        shops_by_country = {}
        for ci, country in enumerate(countries):
            cities = list(country.cities.all())
            made = []
            for i in range(14):
                root = cat_map[Mode.SHOP][(i + ci) % len(cat_map[Mode.SHOP])][0]
                name = f"{SHOP_WORDS[(ci * 3 + i) % len(SHOP_WORDS)]} {SHOP_SUFFIX[(ci + i) % len(SHOP_SUFFIX)]}"
                months = random.choice([1, 2, 5, 7, 11, 14, 20])
                plan = (ShopPlan.TRIAL if months < 3 else
                        ShopPlan.MID if months < 9 else ShopPlan.FULL)
                shop = Shop.objects.create(
                    name=name, country=country, city=random.choice(cities), category=root,
                    about=f"{country.name_local} merkezli mağaza.",
                    hue=HUES[i % len(HUES)], rating=round(random.uniform(3.9, 5.0), 1),
                    sales=random.randint(80, 9000), verified=random.random() > 0.35,
                    plan=plan, opened_at=now - timedelta(days=months * 30),
                )
                made.append(shop)
            shops_by_country[country.code] = made

        # --- ilanlar ---
        bulk = []
        per_sub = opts["per_sub"]
        for country in countries:
            cities = list(country.cities.all())
            for mode in (Mode.USED, Mode.SHOP):
                for root, children, pool, (lo, hi) in cat_map[mode]:
                    for child in children:
                        for n in range(per_sub):
                            base = pool[(n + child.order) % len(pool)]
                            title = (f"{random.choice(ADJ)} {base}" if mode == Mode.USED
                                     else f"{base} · {child.names['tr']}")
                            shop = random.choice(shops_by_country[country.code]) if mode == Mode.SHOP else None
                            bulk.append(Listing(
                                mode=mode, title=title[:200],
                                slug=str(abs(hash(title + country.code + str(n))))[:16],
                                description=(f"{title}. {child.names['tr']} kategorisinde, "
                                             f"{country.name_local} içinde."),
                                price_eur=round(random.uniform(lo, hi), 2),
                                country=country, city=random.choice(cities), category=child,
                                shop=shop,
                                seller_name="" if mode == Mode.SHOP else random.choice(SELLERS),
                                condition="new" if mode == Mode.SHOP else random.choice(["used"] * 4 + ["new"]),
                                delivery=random.choice(["ship", "hand"]),
                                free_shipping=mode == Mode.SHOP and random.random() > 0.5,
                                icon=root.icon, hue=HUES[(child.order + root.order) % len(HUES)],
                                rating=round(random.uniform(3.6, 5.0), 1),
                                favorites=random.randint(3, 320),
                                created_at=now - timedelta(days=random.randint(0, 40),
                                                           hours=random.randint(0, 23)),
                            ))
        Listing.objects.bulk_create(bulk, batch_size=500)

        self.stdout.write(self.style.SUCCESS(
            f"Hazir: {Country.objects.count()} ulke, {City.objects.count()} sehir, "
            f"{Category.objects.count()} kategori, {Shop.objects.count()} magaza, "
            f"{Listing.objects.count()} ilan."
        ))
