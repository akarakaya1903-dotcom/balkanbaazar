from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Category, Listing, Mode, Page


class SmokeTests(TestCase):
    """Temel sayfalarin acildigini ve guvenlik/dil kurallarinin calistigini kontrol eder.
    Calistir:  python manage.py test market"""

    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)

    def test_public_pages_open(self):
        for path in ["/", "/ilanlar/", "/ilanlar/?mode=shop", "/trend/", "/uyelik/giris/", "/uyelik/kayit/", "/robots.txt"]:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_sitemap_index_and_section(self):
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 200)
        self.assertEqual(self.client.get("/sitemap-static.xml").status_code, 200)

    def test_listing_detail_opens(self):
        item = Listing.objects.filter(is_active=True).first()
        self.assertIsNotNone(item)
        self.assertEqual(self.client.get(reverse("market:listing_detail", args=[item.pk, item.slug])).status_code, 200)

    def test_private_pages_need_login(self):
        resp = self.client.get(reverse("market:panel"))
        self.assertEqual(resp.status_code, 302)

    def test_language_prefix_works_and_links_keep_prefix(self):
        resp = self.client.get("/mk/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'href="/mk/')
        self.assertEqual(self.client.get("/mk/ilanlar/").status_code, 200)

    def test_unknown_url_gives_404(self):
        self.assertEqual(self.client.get("/yok-boyle-bir-sayfa/").status_code, 404)

    def test_seo_category_pages(self):
        root = Category.objects.filter(mode=Mode.USED, parent__isnull=True).first()
        self.assertIsNotNone(root)
        self.assertEqual(self.client.get(reverse("market:seo_category", args=["used", root.slug])).status_code, 200)
        self.assertEqual(self.client.get("/kategori/used/olmayan-kategori/").status_code, 302)

    def test_page_translation_fallback(self):
        page = Page(title="TR baslik", body="TR govde",
                    translations={"en": {"title": "EN title", "body": "EN body"}, "bs": {"title": "BS naslov"}})
        self.assertEqual(page.localized("tr"), ("TR baslik", "TR govde"))
        self.assertEqual(page.localized("en"), ("EN title", "EN body"))
        self.assertEqual(page.localized("hr")[0], "BS naslov")
        self.assertEqual(page.localized("mk"), ("EN title", "EN body"))


class FeatureTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)
        call_command("add_pages", verbosity=0)

    def test_attribute_helpers(self):
        from . import attributes as A
        self.assertEqual(A.clean_attrs("vasita", {"attr_year": "2018", "attr_brand": " Fiat ", "attr_fuel": ""}),
                         {"year": 2018, "brand": "Fiat"})
        self.assertEqual(A.clean_attrs("olmayan", {"attr_year": "2018"}), {})
        self.assertEqual(A.choice_label("diesel", "mk"), "Дизел")

    def test_attribute_filter_pages_open(self):
        for qs in ["?mode=used&cat=vasita&a_year_min=2010&a_km_max=200000", "?mode=used&cat=emlak&a_rooms=2%2B1&a_m2_min=50"]:
            with self.subTest(qs=qs):
                self.assertEqual(self.client.get("/ilanlar/" + qs).status_code, 200)

    def test_saved_searches_need_login(self):
        self.assertEqual(self.client.get(reverse("market:saved_searches")).status_code, 302)
        self.assertEqual(self.client.post(reverse("market:save_search"), {"qs": "mode=used"}).status_code, 302)

    def test_help_center_in_languages(self):
        self.assertEqual(self.client.get("/sayfa/yardim-merkezi/").status_code, 200)
        self.assertEqual(self.client.get("/mk/sayfa/yardim-merkezi/").status_code, 200)


class TrustTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)

    def test_verification_doc_is_staff_only(self):
        from django.contrib.auth.models import User
        User.objects.create_user("u1", "u1@example.com", "pw12345678")
        self.client.login(username="u1", password="pw12345678")
        self.assertEqual(self.client.get("/dogrulama-belge/1/").status_code, 404)

    def test_seller_review_needs_conversation(self):
        from django.contrib.auth.models import User
        from .models import UserProfile, can_review_seller
        a = User.objects.create_user("a", "a@example.com", "pw12345678")
        b = User.objects.create_user("b", "b@example.com", "pw12345678")
        UserProfile.objects.create(user=a, email_verified=True)
        self.assertFalse(can_review_seller(a, b))   # henuz mesajlasma yok
        self.assertFalse(can_review_seller(a, a))   # kendini degerlendiremez

    def test_seller_page_and_panel_verification_open(self):
        from django.contrib.auth.models import User
        u = User.objects.create_user("seller", "s@example.com", "pw12345678")
        self.assertEqual(self.client.get(reverse("market:seller_profile", args=[u.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("market:panel_verification")).status_code, 302)


class SearchableFieldTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)

    def test_new_city_is_created_for_application_form(self):
        from .forms import ShopApplicationForm
        from .models import City, Country
        country = Country.objects.first()
        cat = Category.objects.filter(mode=Mode.SHOP, parent__isnull=True).first()
        data = {"shop_name": "Test Magaza", "country": country.pk, "category": cat.pk, "contact_name": "A B",
                "email": "a@example.com", "phone": "+38970000000", "city_new": "Yeni Sehir Adi"}
        form = ShopApplicationForm(data)
        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save(commit=False)
        self.assertEqual(obj.city.name, "Yeni Sehir Adi")
        self.assertIsNotNone(obj.city.pk)
        self.assertEqual(City.objects.filter(country=country, name="Yeni Sehir Adi").count(), 1)

    def test_bad_city_name_rejected(self):
        from .forms import ShopApplicationForm
        from .models import Country
        country = Country.objects.first()
        cat = Category.objects.filter(mode=Mode.SHOP, parent__isnull=True).first()
        form = ShopApplicationForm({"shop_name": "T", "country": country.pk, "category": cat.pk, "contact_name": "A",
                                    "email": "a@example.com", "phone": "1", "city_new": "<script>"})
        self.assertFalse(form.is_valid())


class PixelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)

    def test_pixel_only_when_configured(self):
        from .models import SiteSettings
        self.assertNotContains(self.client.get("/"), "fbevents.js")
        SiteSettings.objects.create(meta_pixel_id="123456789012345")
        resp = self.client.get("/")
        self.assertContains(resp, "fbevents.js")
        self.assertContains(resp, "123456789012345")
        self.assertContains(resp, "bbConsentLoad")  # onay verilmeden yuklenmez: yukleme bbConsentLoad ile tetiklenir


class ApprovalTests(TestCase):
    """Onay bekleyen ilan yayina girmez; yenile butonuyla onay atlatilamaz."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)

    def test_pending_listing_is_not_public_and_cannot_be_renewed(self):
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create_user("satici", "s@example.com", "pw12345678")
        base = Listing.objects.filter(is_active=True, mode=Mode.USED).first()
        item = Listing.objects.create(
            mode=Mode.USED, title="Bekleyen ilan", price_eur=10, country=base.country,
            category=base.category, owner=user, is_active=False, pending_review=True,
        )
        self.assertNotIn(item, Listing.objects.filter(is_active=True))
        self.client.force_login(user)
        self.client.post(reverse("market:renew_listing", args=[item.pk]))
        item.refresh_from_db()
        self.assertFalse(item.is_active)
        self.assertTrue(item.pending_review)

    def test_pending_detail_hidden_from_public_visible_to_owner(self):
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create_user("satici2", "s2@example.com", "pw12345678")
        base = Listing.objects.filter(is_active=True, mode=Mode.USED).first()
        item = Listing.objects.create(
            mode=Mode.USED, title="Gizli bekleyen", price_eur=10, country=base.country,
            category=base.category, owner=user, is_active=False, pending_review=True,
        )
        url = reverse("market:listing_detail", args=[item.pk, item.slug])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(user)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_approval_messages_in_all_languages(self):
        from .i18n import LANGUAGES, T
        for code, _ in LANGUAGES:
            for key in ("stat_pending", "apply_received", "listing_pending", "product_pending", "pending_note"):
                with self.subTest(lang=code, key=key):
                    self.assertTrue(T[code].get(key))


class StaffTwoFactorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)

    def test_totp_rfc_vector_and_replay(self):
        import base64
        from . import totp
        sec = base64.b32encode(b"12345678901234567890").decode()
        self.assertEqual(totp.verify(sec, "287082", 0, now=59), 1)
        self.assertIsNone(totp.verify(sec, "287082", 1, now=59))
        self.assertIsNone(totp.verify(sec, "000000", 0, now=59))

    def test_staff_must_pass_2fa_for_admin_and_panel(self):
        import time
        from django.contrib.auth import get_user_model
        from . import totp
        from .models import StaffTOTP
        staff = get_user_model().objects.create_user("yonetici", "y@example.com", "pw12345678", is_staff=True, is_superuser=True)
        self.client.force_login(staff)
        for path in ("/admin/", "/yonetim/"):
            with self.subTest(path=path):
                r = self.client.get(path)
                self.assertEqual(r.status_code, 302)
                self.assertTrue(r["Location"].startswith("/uyelik/iki-adim/"))
        # kurulum sayfasi acilir, yanlis kod reddedilir, dogru kod gecirir
        self.assertEqual(self.client.get("/uyelik/iki-adim/").status_code, 200)
        dev = StaffTOTP.objects.get(user=staff)
        self.client.post("/uyelik/iki-adim/", {"code": "000000"})
        self.assertEqual(self.client.get("/admin/").status_code, 302)
        code = totp._code(dev.secret, int(time.time() // 30))
        r = self.client.post("/uyelik/iki-adim/", {"code": code, "next": "/admin/"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.client.get("/admin/").status_code, 200)

    def test_normal_user_not_affected_and_health_ok(self):
        self.assertEqual(self.client.get("/saglik/").content, b"ok")
        self.assertEqual(self.client.get("/").status_code, 200)


class VisitorCounterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)

    def test_same_browser_counts_once_and_ignore_cookie(self):
        from .models import DailyStat
        self.client.get("/")
        self.client.get("/")
        stat = DailyStat.objects.first()
        self.assertEqual(stat.new_visitors, 1)
        self.assertEqual(stat.visitors, 1)
        self.assertEqual(stat.pageviews, 2)
        from django.test import Client
        c2 = Client()
        c2.get("/?bb_ignore=1")
        c2.get("/")
        stat.refresh_from_db()
        self.assertEqual(stat.new_visitors, 1)   # yoksayilan tarayici sayilmadi


class SiteCleanupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)

    def test_empty_shop_hidden_from_public_lists_and_sitemap(self):
        from .models import Country, Shop, Listing
        c = Country.objects.get(code="MK")
        empty = Shop.objects.create(name="Bos Magaza Testi", country=c)
        self.assertNotIn(empty, Shop.objects.listed())
        body = self.client.get("/magazalar/").content.decode()
        self.assertNotIn("Bos Magaza Testi", body)
        self.assertNotIn(empty.slug, self.client.get("/sitemap-shops.xml").content.decode())
        # urunu onay bekliyorsa hala gizli, yayina girince gorunur
        base = Listing.objects.filter(mode=Mode.SHOP, is_active=True).first()
        item = Listing.objects.create(mode=Mode.SHOP, title="Test urun", price_eur=5, country=c,
                                      category=base.category, shop=empty, is_active=False, pending_review=True)
        self.assertNotIn(empty, Shop.objects.listed())
        item.is_active, item.pending_review = True, False
        item.save()
        self.assertIn(empty, Shop.objects.listed())

    def test_country_names_localized(self):
        from .models import Country
        mk = Country.objects.get(code="MK")
        self.assertEqual(mk.display_name("mk"), "Северна Македонија")
        self.assertEqual(mk.display_name("sq"), "Maqedonia e Veriut")
        self.assertEqual(mk.display_name("tr"), mk.name_tr)

    def test_home_meta_uses_language_specific_text_not_turkish_override(self):
        from .models import SiteSettings
        ss = SiteSettings.objects.first() or SiteSettings.objects.create()
        ss.seo_title = "TURKCE OZEL BASLIK"
        ss.seo_description = "TURKCE OZEL ACIKLAMA"
        ss.save()
        self.assertContains(self.client.get("/tr/"), "TURKCE OZEL BASLIK")
        self.assertNotContains(self.client.get("/en/"), "TURKCE OZEL BASLIK")
        self.assertNotContains(self.client.get("/mk/"), "TURKCE OZEL ACIKLAMA")

    def test_stats_strip_hidden_when_few_listings(self):
        from django.test import override_settings
        with override_settings(STATS_MIN_LISTINGS=10**9):
            self.assertNotContains(self.client.get("/tr/"), "hero2-stats")
        with override_settings(STATS_MIN_LISTINGS=1):
            self.assertContains(self.client.get("/tr/"), "hero2-stats")


class ListingCurrencyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)

    def _form(self, country_code, amount, currency):
        from .forms import IndividualListingForm
        from .models import Country
        c = Country.objects.get(code=country_code)
        cat = Category.objects.filter(mode=Mode.USED, parent__isnull=False).first()
        data = {"title": "Test", "category": cat.pk, "price_input": amount,
                "price_currency": currency, "condition": "used", "delivery": "hand"}
        return IndividualListingForm(data, country=c), c

    def test_mkd_price_kept_as_entered_and_converted_to_eur(self):
        form, c = self._form("MK", "6000", "MKD")
        self.assertTrue(form.is_valid(), form.errors)
        item = form.save(commit=False)
        self.assertEqual(item.price_currency, "MKD")
        self.assertEqual(float(item.price_input), 6000.0)
        self.assertAlmostEqual(float(item.price_eur), 6000 / float(c.rate_per_eur), places=1)
        self.assertIn("6.000", item.display_price())      # girilen fiyat aynen gorunur
        self.assertTrue(item.alt_price().startswith("≈ €"))

    def test_eur_price_in_mk(self):
        form, c = self._form("MK", "100", "EUR")
        self.assertTrue(form.is_valid(), form.errors)
        item = form.save(commit=False)
        self.assertEqual(float(item.price_eur), 100.0)
        self.assertEqual(item.display_price(), "€ 100")

    def test_currency_choices_follow_country(self):
        form, c = self._form("MK", "10", "EUR")
        codes = [k for k, _ in form.fields["price_currency"].choices]
        self.assertEqual(codes, [c.currency, "EUR"])
        bad, _ = self._form("MK", "10", "USD")
        self.assertFalse(bad.is_valid())

    def test_legacy_listing_without_input_still_converts(self):
        item = Listing.objects.filter(mode=Mode.USED).first()
        item.price_input, item.price_currency = None, ""
        self.assertEqual(item.display_price(), item.country.format_price(item.price_eur))


class ProductCurrencyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)

    def test_shop_product_price_in_local_currency(self):
        from .forms import ProductForm
        from .models import Shop
        shop = Shop.objects.filter(country__code="MK").first()
        cat = Category.objects.filter(mode=Mode.SHOP, parent__isnull=False).first()
        form = ProductForm({"title": "Urun", "category": cat.pk, "price_input": "3000",
                            "price_currency": "MKD", "delivery": "hand"}, shop=shop)
        self.assertTrue(form.is_valid(), form.errors)
        item = form.save(commit=False)
        self.assertEqual(item.price_currency, "MKD")
        self.assertAlmostEqual(float(item.price_eur), 3000 / float(shop.country.rate_per_eur), places=1)
        self.assertIn("3.000", item.display_price())


class CategorySeoTextTests(TestCase):
    def test_seo_text_all_languages(self):
        from .i18n import seo_text
        for lang in ["tr", "en", "mk", "sq", "sr", "bs", "hr", "cnr", "bg", "el", "xx"]:
            for mode in ("used", "shop"):
                title, desc = seo_text(lang, mode, "Kategori", "Skopje")
                self.assertIn("Kategori", title)
                self.assertIn("Skopje", desc)
                self.assertLessEqual(len(desc), 160)
