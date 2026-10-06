from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Mode(models.TextChoices):
    USED = "used", "Ikinci el"
    SHOP = "shop", "Magaza"


class Country(models.Model):
    """8 Balkan ulkesi. Para birimi ve kur burada tutulur."""
    code = models.CharField(max_length=2, primary_key=True)
    name_local = models.CharField(max_length=60)
    name_tr = models.CharField(max_length=60)
    name_en = models.CharField(max_length=60)
    flag = models.CharField(max_length=8)
    lang = models.CharField(max_length=5, default="en")
    currency = models.CharField(max_length=3)
    symbol = models.CharField(max_length=6)
    rate_per_eur = models.DecimalField(max_digits=12, decimal_places=4, default=1)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "code"]
        verbose_name_plural = "countries"

    def __str__(self):
        return f"{self.flag} {self.name_local}"

    def display_name(self, lang="tr"):
        """Ulke adini secili dile gore dondurur."""
        if lang == "tr":
            return self.name_tr
        if lang == "en":
            return self.name_en
        return self.name_local

    def to_local(self, eur):
        return float(eur) * float(self.rate_per_eur)

    def format_price(self, eur):
        value = self.to_local(eur)
        text = f"{value:,.0f}".replace(",", ".")
        if self.currency == "EUR":
            return f"€ {text}"
        return f"{text} {self.symbol}"


class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=80)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        unique_together = [("country", "name")]
        verbose_name_plural = "cities"

    def __str__(self):
        return f"{self.name} ({self.country_id})"


class Category(models.Model):
    """Ana kategori ve alt kategori ayni modelde (parent ile)."""
    mode = models.CharField(max_length=8, choices=Mode.choices)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    slug = models.SlugField(max_length=80)
    icon = models.CharField(max_length=8, blank=True)
    image = models.ImageField("Gorsel (istege bagli)", upload_to="categories/", blank=True, null=True,
                              help_text="Yuklenirse ana sayfa kutusunda simge yerine bu fotograf gorunur.")
    names = models.JSONField(default=dict, help_text='{"tr": "...", "en": "...", ...}')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        unique_together = [("mode", "parent", "slug")]
        verbose_name_plural = "categories"

    def __str__(self):
        return f"[{self.mode}] {self.name('tr')}"

    def name(self, lang="tr"):
        return self.names.get(lang) or self.names.get("en") or self.slug

    @property
    def is_root(self):
        return self.parent_id is None


class ShopPlan(models.TextChoices):
    TRIAL = "trial", "Ilk 3 ay ucretsiz"
    MID = "mid", "9 EUR / ay"
    FULL = "full", "29 EUR / ay"


class Shop(models.Model):
    owner = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="shops"
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="shops")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="shops"
    )
    logo = models.ImageField(upload_to="shops/", blank=True, null=True)
    about = models.TextField(blank=True)
    hue = models.PositiveSmallIntegerField(default=190)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    sales = models.PositiveIntegerField(default=0)
    verified = models.BooleanField(default=False)
    plan = models.CharField(max_length=8, choices=ShopPlan.choices, default=ShopPlan.TRIAL)
    opened_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-verified", "-rating", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.name}-{self.country_id}")
            self.slug = base[:140]
        super().save(*args, **kwargs)

    @property
    def months_open(self):
        delta = timezone.now() - self.opened_at
        return delta.days // 30

    @property
    def monthly_fee_eur(self):
        """Hibrit fiyatlandirma: 0-3 ay bedava, 4-9 ay 9 EUR, sonrasi 29 EUR."""
        m = self.months_open
        if m < settings.SHOP_PLAN_FREE_MONTHS:
            return 0
        if m < settings.SHOP_PLAN_MID_UNTIL_MONTH:
            return settings.SHOP_PLAN_MID_PRICE_EUR
        return settings.SHOP_PLAN_FULL_PRICE_EUR

    @property
    def product_count(self):
        return self.listings.count()


class Condition(models.TextChoices):
    NEW = "new", "Sifir"
    USED = "used", "Ikinci el"


class Delivery(models.TextChoices):
    SHIP = "ship", "Kargo"
    HAND = "hand", "Elden teslim"


def _shrink(fieldfile, max_side=1600, quality=82):
    """Yuklenen fotografi sunucuda kucultur ve JPEG olarak yeniden sikistirir. Hata olursa orijinali birakir."""
    try:
        import os
        from io import BytesIO

        from django.core.files.base import ContentFile
        from PIL import Image, ImageOps
        fieldfile.seek(0)
        im = ImageOps.exif_transpose(Image.open(fieldfile))
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")
        im.thumbnail((max_side, max_side), Image.LANCZOS)
        buf = BytesIO()
        im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        name = os.path.splitext(os.path.basename(fieldfile.name))[0] + ".jpg"
        return ContentFile(buf.getvalue(), name=name)
    except Exception:
        try:
            fieldfile.seek(0)
        except Exception:
            pass
        return fieldfile


class Listing(models.Model):
    """Hem ikinci el ilani hem magaza urunu."""
    mode = models.CharField(max_length=8, choices=Mode.choices, db_index=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    description = models.TextField(blank=True)
    price_eur = models.DecimalField(max_digits=12, decimal_places=2)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="listings")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="listings",
        help_text="Alt kategori secilir",
    )
    shop = models.ForeignKey(
        Shop, null=True, blank=True, on_delete=models.CASCADE, related_name="listings"
    )
    owner = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="my_listings",
        help_text="Bireysel (ikinci el) ilanin sahibi",
    )
    image = models.ImageField(upload_to="listings/", blank=True, null=True)
    video = models.FileField("Video (mp4/webm, en fazla 50 MB)", upload_to="listings/video/", blank=True, null=True)
    video_processed = models.BooleanField(default=False, editable=False)  # sunucuda kucultuldu mu
    attrs = models.JSONField(default=dict, blank=True)  # kategoriye ozel alanlar (marka, yil, km, oda sayisi ...)
    featured_until = models.DateTimeField(null=True, blank=True, db_index=True)
    track_stock = models.BooleanField(default=False, help_text="Acilirsa stok adedi tukeninceye kadar satisa acik kalir")
    stock = models.PositiveIntegerField(null=True, blank=True, help_text="track_stock acikken gecerli")
    seller_name = models.CharField(max_length=80, blank=True)
    seller_phone = models.CharField(max_length=32, blank=True)
    condition = models.CharField(max_length=8, choices=Condition.choices, default=Condition.USED)
    delivery = models.CharField(max_length=8, choices=Delivery.choices, default=Delivery.HAND)
    free_shipping = models.BooleanField(default=False)
    icon = models.CharField(max_length=8, blank=True)
    hue = models.PositiveSmallIntegerField(default=190)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    favorites = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    pending_review = models.BooleanField("Onay bekliyor", default=False, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["mode", "country", "category"])]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220] or "ilan"
        if self.image and not getattr(self.image, "_committed", True):
            self.image = _shrink(self.image)
        if self.video and not getattr(self.video, "_committed", True):
            self.video_processed = False
        super().save(*args, **kwargs)

    @property
    def parent_category(self):
        return self.category.parent or self.category

    def local_price(self, country=None):
        return (country or self.country).format_price(self.price_eur)

    @property
    def age_days(self):
        return (timezone.now() - self.created_at).days

    @property
    def is_boosted(self):
        return bool(self.featured_until and self.featured_until >= timezone.now())

    @property
    def in_stock(self):
        if not self.track_stock:
            return True
        if self.variants.exists():
            return any(v.stock > 0 for v in self.variants.all())
        return (self.stock or 0) > 0

    @property
    def avg_rating(self):
        agg = self.reviews.aggregate(a=models.Avg("rating"))["a"]
        return round(agg, 1) if agg else None

    @property
    def review_count(self):
        return self.reviews.count()


class ApplicationStatus(models.TextChoices):
    PENDING = "pending", "Beklemede"
    APPROVED = "approved", "Onaylandi"
    REJECTED = "rejected", "Reddedildi"


class ShopApplication(models.Model):
    """Magaza acma basvurusu. Onaylaninca Shop kaydi olusur."""
    applicant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shop_applications"
    )
    shop_name = models.CharField(max_length=120)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={"mode": Mode.SHOP, "parent__isnull": True},
    )
    contact_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    tax_number = models.CharField(max_length=40, blank=True)
    website = models.URLField(blank=True)
    about = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=ApplicationStatus.choices, default=ApplicationStatus.PENDING
    )
    staff_note = models.TextField(blank=True)
    shop = models.OneToOneField(
        Shop, null=True, blank=True, on_delete=models.SET_NULL, related_name="application"
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.shop_name} ({self.get_status_display()})"

    def approve(self):
        """Basvuruyu onayla: magazayi olustur, ilk 3 ay ucretsiz paketle baslat."""
        if self.shop:
            return self.shop
        shop = Shop.objects.create(
            owner=self.applicant, name=self.shop_name, country=self.country,
            city=self.city, category=self.category, about=self.about,
            plan=ShopPlan.TRIAL, opened_at=timezone.now(), rating=0, hue=190,
        )
        self.shop = shop
        self.status = ApplicationStatus.APPROVED
        self.save(update_fields=["shop", "status"])
        return shop


class ListingImage(models.Model):
    """Bir urune ait ek gorseller (kapak disinda)."""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="listings/gallery/")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        if self.image and not getattr(self.image, "_committed", True):
            self.image = _shrink(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.listing_id} - #{self.order}"


# ---------------------------------------------------------------------------
# Siparis / sepet
# ---------------------------------------------------------------------------
class OrderStatus(models.TextChoices):
    PENDING = "pending", "Beklemede"
    PAID = "paid", "Odendi"
    CANCELLED = "cancelled", "Iptal"


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=10, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_eur = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    full_name = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=240, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    stripe_session_id = models.CharField(max_length=200, blank=True)
    payment_method = models.CharField(max_length=10, default="card")  # card | cod (kapida odeme)
    paid_at = models.DateTimeField(null=True, blank=True)
    coupon = models.ForeignKey("Coupon", null=True, blank=True, on_delete=models.SET_NULL)
    discount_eur = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} — {self.buyer}"

    @property
    def is_shipped(self):
        return self.items.exists() and all(it.shipped_at for it in self.items.all())

    @property
    def can_cancel(self):
        return self.status == OrderStatus.PAID and not any(it.shipped_at for it in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    listing = models.ForeignKey(Listing, null=True, blank=True, on_delete=models.SET_NULL)
    variant = models.ForeignKey(
        "ListingVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="order_items"
    )
    shop = models.ForeignKey(Shop, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200)
    variant_name = models.CharField(max_length=60, blank=True)
    price_eur = models.DecimalField(max_digits=12, decimal_places=2)
    qty = models.PositiveSmallIntegerField(default=1)
    carrier = models.CharField(max_length=60, blank=True)
    tracking_number = models.CharField(max_length=80, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)

    @property
    def line_total_eur(self):
        return self.price_eur * self.qty


# ---------------------------------------------------------------------------
# Mesajlasma
# ---------------------------------------------------------------------------
class Conversation(models.Model):
    listing = models.ForeignKey(
        Listing, null=True, blank=True, on_delete=models.SET_NULL, related_name="conversations"
    )
    participant_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conv_a")
    participant_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conv_b")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = [("listing", "participant_a", "participant_b")]

    def other(self, user):
        return self.participant_b if user == self.participant_a else self.participant_a

    def last_message(self):
        return self.messages.order_by("-created_at").first()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)  # alicıya e-posta gonderildi mi
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]


class BoostStatus(models.TextChoices):
    PENDING = "pending", "Beklemede"
    PAID = "paid", "Odendi"


class Boost(models.Model):
    """Ilan/urun one cikarma satin alimi (ucretli vitrin)."""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="boosts")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boosts")
    days = models.PositiveSmallIntegerField()
    price_eur = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=BoostStatus.choices, default=BoostStatus.PENDING)
    stripe_session_id = models.CharField(max_length=200, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Boost #{self.pk} — {self.listing.title} ({self.days}g)"

    def apply(self):
        """Odeme onaylaninca ilanin vitrin suresini uzatir."""
        from datetime import timedelta
        base = self.listing.featured_until
        start = base if base and base > timezone.now() else timezone.now()
        self.listing.featured_until = start + timedelta(days=self.days)
        self.listing.save(update_fields=["featured_until"])
        self.status = BoostStatus.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])


# ---------------------------------------------------------------------------
# Varyant (beden / renk vb.)
# ---------------------------------------------------------------------------
class ListingVariant(models.Model):
    """Bir urunun beden/renk gibi secenekleri, her birinin kendi stogu."""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=60, help_text="orn. 'Kırmızı / M'")
    price_delta_eur = models.DecimalField(max_digits=8, decimal_places=2, default=0,
                                          help_text="Ana fiyata eklenir/cikarilir, orn. -2.00")
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=40, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.listing.title} — {self.name}"

    @property
    def final_price_eur(self):
        return self.listing.price_eur + self.price_delta_eur


# ---------------------------------------------------------------------------
# Favoriler
# ---------------------------------------------------------------------------
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    listing = models.ForeignKey(Listing, null=True, blank=True, on_delete=models.CASCADE, related_name="favorited_by")
    shop = models.ForeignKey(Shop, null=True, blank=True, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "listing"], name="uniq_fav_listing",
                                    condition=models.Q(listing__isnull=False)),
            models.UniqueConstraint(fields=["user", "shop"], name="uniq_fav_shop",
                                    condition=models.Q(shop__isnull=False)),
        ]


# ---------------------------------------------------------------------------
# Degerlendirme / yorum (yalniz onaylanmis satin alimdan)
# ---------------------------------------------------------------------------
class Review(models.Model):
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name="review")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.listing.title} — {self.rating}★"


# ---------------------------------------------------------------------------
# Kupon
# ---------------------------------------------------------------------------
class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    shop = models.ForeignKey(Shop, null=True, blank=True, on_delete=models.CASCADE, related_name="coupons",
                             help_text="Bossa tum magazalarda gecerli")
    percent_off = models.PositiveSmallIntegerField(null=True, blank=True, help_text="orn. 20 -> %20 indirim")
    amount_off_eur = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    active = models.BooleanField(default=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        if not self.active:
            return False
        if self.valid_until and self.valid_until < timezone.now():
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True

    def discount_for(self, subtotal_eur):
        if self.percent_off:
            return subtotal_eur * self.percent_off / 100
        if self.amount_off_eur:
            return min(self.amount_off_eur, subtotal_eur)
        return 0


class SiteSettings(models.Model):
    """Tek kayitlik site ayarlari (admin panelinden duzenlenir)."""
    hero_image = models.ImageField(
        "Ana sayfa banner gorseli", upload_to="site/", blank=True, null=True,
        help_text="Bos birakilirsa varsayilan cizim banner kullanilir. Genis (en az 1600 px) bir fotograf onerilir.",
    )

    seo_title = models.CharField("Google basligi (ana sayfa)", max_length=70, blank=True,
                                 help_text="Google sonucunda mavi baslik olarak gorunur. Bos birakirsan varsayilan kullanilir.")
    seo_description = models.CharField("Google aciklamasi (ana sayfa)", max_length=170, blank=True,
                                       help_text="Basligin altindaki tanitim yazisi, 150-160 karakter ideal.")
    moderate_new_listings = models.BooleanField("Yeni bireysel ilanlar yonetici onayindan gecsin", default=False,
                                                help_text="Acikken yeni ilanlar yayina girmeden once Ilanlar listesinde 'Onay bekliyor' olarak gorunur.")
    meta_pixel_id = models.CharField("Meta (Facebook/Instagram) Piksel kimligi", max_length=20, blank=True,
                                     help_text="Sadece rakamlar (orn. 123456789012345). Bos birakirsan piksel yuklenmez. Yalnizca cerez onayi veren ziyaretcilerde calisir.")
    meta_domain_verification = models.CharField("Meta alan adi dogrulama kodu", max_length=80, blank=True,
                                                help_text="Meta Business > Marka guvenligi > Alan adlari ekraninda verilen meta etiketi kodu.")
    analytics_id = models.CharField("Google Analytics olcum kimligi", max_length=30, blank=True,
                                    help_text="Ornek: G-XXXXXXXXXX. Bos birakirsan analiz kodu eklenmez.")
    company_name = models.CharField("Sirket adi", max_length=160, blank=True,
                                    help_text="Alt bilgide (c) satirinda gorunur.")
    address = models.TextField("Adres", blank=True)
    email = models.EmailField("E-posta", blank=True)
    phone = models.CharField("Telefon", max_length=40, blank=True)

    class Meta:
        verbose_name = "Site ayari"
        verbose_name_plural = "Site ayarlari"

    def __str__(self):
        return "Site ayarlari"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class Banner(models.Model):
    """Reklam / kampanya banner'i (Trendyol tarzi kaydirici ve orta serit)."""
    PLACES = [("home_hero", "Ana sayfa ust kaydirici (1400x420 onerilir)"),
              ("home_mid", "Ana sayfa orta serit (600x300 onerilir, en fazla 3)")]
    title = models.CharField("Baslik", max_length=120)
    advertiser = models.CharField("Reklamveren", max_length=120, blank=True)
    image = models.ImageField("Gorsel (web / bilgisayar)", upload_to="banners/")
    image_mobile = models.ImageField("Gorsel (telefon / Android, istege bagli)", upload_to="banners/", blank=True, null=True,
                                     help_text="16:9 (orn. 1280x720). Bos birakirsan telefonda da web gorseli kullanilir.")
    link_url = models.CharField("Tiklayinca gidilecek adres", max_length=300, blank=True)
    place = models.CharField("Alan", max_length=12, choices=PLACES, default="home_hero")
    order = models.PositiveSmallIntegerField("Sira", default=0)
    is_active = models.BooleanField("Yayinda", default=True)
    starts_at = models.DateTimeField("Baslangic", null=True, blank=True)
    ends_at = models.DateTimeField("Bitis", null=True, blank=True)
    clicks = models.PositiveIntegerField("Tiklama", default=0, editable=False)

    class Meta:
        ordering = ["place", "order", "-id"]
        verbose_name = "Reklam banner"
        verbose_name_plural = "Reklam bannerlari"

    def __str__(self):
        return f"{self.title} ({self.get_place_display()})"


class Page(models.Model):
    """Alt bilgideki sayfalar: Hakkimizda, Iletisim, Kullanim kosullari vb."""
    GROUPS = [("f1", "Kurumsal sutunu"), ("f2", "Yardim sutunu")]
    title = models.CharField("Baslik", max_length=120)
    slug = models.SlugField("Adres (slug)", max_length=140, unique=True)
    body = models.TextField("Icerik", help_text="Duz metin. Bos satir yeni paragraf olur.")
    group = models.CharField("Alt bilgide yeri", max_length=2, choices=GROUPS, default="f1")
    order = models.PositiveSmallIntegerField("Sira", default=0)
    is_published = models.BooleanField("Yayinda", default=True)
    translations = models.JSONField("Ceviriler", default=dict, blank=True,
                                    help_text='Ornek: {"mk": {"title": "...", "body": "..."}}. Dil kodlari: en, mk, sq, sr, bg, el, bs.')

    def localized(self, lang):
        """(baslik, icerik): once secili dil, sonra Ingilizce, sonra Turkce (ana alan)."""
        if lang == "tr":
            return self.title, self.body
        tr = self.translations or {}

        def pick(field):
            for code in (lang, {"hr": "bs", "cnr": "bs"}.get(lang, lang), "en"):
                value = (tr.get(code) or {}).get(field)
                if value:
                    return value
            return getattr(self, field)
        return pick("title"), pick("body")

    class Meta:
        ordering = ["group", "order", "title"]
        verbose_name = "Sayfa"
        verbose_name_plural = "Sayfalar"

    def __str__(self):
        return self.title


class DailyStat(models.Model):
    """Gunluk tekil ziyaretci ve sayfa goruntuleme sayaci (kisisel veri tutmaz)."""
    day = models.DateField("Gun", unique=True)
    visitors = models.PositiveIntegerField("Tekil ziyaretci", default=0)
    pageviews = models.PositiveIntegerField("Sayfa goruntuleme", default=0)

    class Meta:
        ordering = ["-day"]
        verbose_name = "Gunluk istatistik"
        verbose_name_plural = "Gunluk istatistikler"

    def __str__(self):
        return f"{self.day}: {self.visitors}"


class ListingReport(models.Model):
    """Kullanicilarin ilanlar hakkinda yaptigi sikayetler."""
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="reports_made")
    message = models.TextField("Sikayet metni", max_length=1000)
    created_at = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField("Cozuldu", default=False)

    class Meta:
        ordering = ["resolved", "-created_at"]
        verbose_name = "Ilan sikayeti"
        verbose_name_plural = "Ilan sikayetleri"

    def __str__(self):
        return f"#{self.pk} {self.listing_id}"


class UserProfile(models.Model):
    """Uyeye ait ek bilgiler (su an: e-posta dogrulama durumu)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} ({'dogrulandi' if self.email_verified else 'dogrulanmadi'})"


def email_is_verified(user):
    if user.is_staff:
        return True
    prof = UserProfile.objects.filter(user=user).first()
    return bool(prof and prof.email_verified)


class UserBlock(models.Model):
    """Bir kullanicinin baska bir kullaniciyi engellemesi (mesajlasma iki yone de kapanir)."""
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocks_made")
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocks_received")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("blocker", "blocked")]
        verbose_name = "Engelleme"
        verbose_name_plural = "Engellemeler"

    def __str__(self):
        return f"{self.blocker} -> {self.blocked}"


class PushSubscription(models.Model):
    """Tarayici/telefon anlik bildirim abonelikleri (Web Push)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="push_subscriptions")
    endpoint = models.CharField(max_length=600, unique=True)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} ({self.endpoint[:40]}...)"


class SavedSearch(models.Model):
    """Kullanicinin kayitli aramasi; yeni eslesen ilan gelince bildirim gider."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_searches")
    label = models.CharField(max_length=120)
    params = models.CharField(max_length=500)  # ornek: mode=used&cat=vasita&a_year_min=2015
    country = models.ForeignKey("Country", null=True, blank=True, on_delete=models.SET_NULL)
    mode = models.CharField(max_length=10, default="used")
    created_at = models.DateTimeField(default=timezone.now)
    last_checked = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("user", "params")]
        verbose_name = "Kayitli arama"
        verbose_name_plural = "Kayitli aramalar"

    def __str__(self):
        return f"{self.user}: {self.label}"


def get_private_storage():
    from django.conf import settings
    from django.core.files.storage import FileSystemStorage
    return FileSystemStorage(location=str(settings.PRIVATE_ROOT))


def _verify_path(instance, filename):
    import os
    import uuid
    return f"verify/{uuid.uuid4().hex}{os.path.splitext(filename)[1].lower()}"


class VerificationRequest(models.Model):
    """Magaza dogrulama basvurusu (belge herkese kapali klasorde saklanir)."""
    STATUS = [("pending", "Beklemede"), ("approved", "Onaylandi"), ("rejected", "Reddedildi")]
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="verification_requests")
    document = models.FileField(upload_to=_verify_path, storage=get_private_storage)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    admin_note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Dogrulama basvurusu"
        verbose_name_plural = "Dogrulama basvurulari"

    def __str__(self):
        return f"{self.shop} ({self.get_status_display()})"


class SellerReview(models.Model):
    """Bireysel saticilar icin degerlendirme (yalnizca mesajlasmis, e-postasi dogrulanmis uyeler)."""
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_reviews")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_reviews_written")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = [("seller", "author")]
        ordering = ["-created_at"]
        verbose_name = "Satici degerlendirmesi"
        verbose_name_plural = "Satici degerlendirmeleri"

    def __str__(self):
        return f"{self.author} -> {self.seller}: {self.rating}"


def seller_rating(user):
    agg = SellerReview.objects.filter(seller=user).aggregate(a=models.Avg("rating"), n=models.Count("id"))
    return (round(agg["a"], 1) if agg["a"] else None, agg["n"])


def can_review_seller(author, seller):
    """Kendisi olmayan, e-postasi dogrulanmis ve satici ile karsilikli mesajlasmis uye."""
    if not getattr(author, "is_authenticated", False) or author.pk == seller.pk or not email_is_verified(author):
        return False
    if SellerReview.objects.filter(author=author, seller=seller).exists():
        return False
    convs = Conversation.objects.filter(models.Q(participant_a=author, participant_b=seller) |
                                        models.Q(participant_a=seller, participant_b=author))
    return (Message.objects.filter(conversation__in=convs, sender=author).exists()
            and Message.objects.filter(conversation__in=convs, sender=seller).exists())


from django.db.models.signals import post_delete, post_save  # noqa: E402
from django.dispatch import receiver  # noqa: E402


@receiver([post_save, post_delete], sender=Review)
def _update_ratings(sender, instance, **kwargs):
    """Yorum eklenince/silinince ilanin ve magazanin puanini gercek yorum ortalamasina gunceller (yorum yoksa 0)."""
    try:
        from decimal import Decimal
        listing = instance.listing
        avg = Review.objects.filter(listing=listing).aggregate(a=models.Avg("rating"))["a"]
        Listing.objects.filter(pk=listing.pk).update(rating=Decimal(str(round(avg, 1))) if avg else 0)
        if listing.shop_id:
            avg = Review.objects.filter(listing__shop_id=listing.shop_id).aggregate(a=models.Avg("rating"))["a"]
            Shop.objects.filter(pk=listing.shop_id).update(rating=Decimal(str(round(avg, 1))) if avg else 0)
    except Exception:
        pass
