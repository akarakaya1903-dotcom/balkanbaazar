from django.conf import settings
# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (Category, City, Listing, ListingImage, ListingVariant, Mode,
                     Shop, ShopApplication)


class VideoCleanMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "video" in self.fields:
            self.fields["video"].label = "Video (mp4, mov, webm)"
            self.fields["video"].help_text = (
                f"En fazla {settings.MAX_VIDEO_SECONDS // 60} dakika / {settings.MAX_VIDEO_MB} MB. "
                "Yukleme internet hizina gore birkac dakika surebilir, sayfayi kapatma.")

    def clean_video(self):
        v = self.cleaned_data.get("video")
        if v and hasattr(v, "size"):
            if not v.name.lower().endswith((".mp4", ".webm", ".mov")):
                raise forms.ValidationError("Sadece mp4, webm veya mov yukleyebilirsin.")
            if v.size > settings.MAX_VIDEO_MB * 1024 * 1024:
                raise forms.ValidationError(f"Video en fazla {settings.MAX_VIDEO_MB} MB olabilir.")
        return v


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=60, required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu e-posta ile bir hesap zaten var.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        if commit:
            user.save()
        return user


class ShopApplicationForm(forms.ModelForm):
    class Meta:
        model = ShopApplication
        fields = ("shop_name", "country", "city", "category", "contact_name",
                  "email", "phone", "tax_number", "website", "about")
        widgets = {"about": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(
            mode=Mode.SHOP, parent__isnull=True
        )
        self.fields["city"].queryset = City.objects.select_related("country")
        self.fields["city"].required = False


class ShopSettingsForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ("name", "logo", "city", "category", "about")
        widgets = {"about": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        shop = self.instance
        self.fields["city"].queryset = City.objects.filter(country=shop.country)
        self.fields["category"].queryset = Category.objects.filter(
            mode=Mode.SHOP, parent__isnull=True
        )


class ProductForm(VideoCleanMixin, forms.ModelForm):
    """Magaza sahibinin urun formu. mode/country/shop otomatik doldurulur."""

    class Meta:
        model = Listing
        fields = ("title", "category", "price_eur", "city", "description", "image", "video",
                  "delivery", "free_shipping", "is_active", "track_stock", "stock")
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}
        labels = {
            "title": "Urun adi", "category": "Kategori", "price_eur": "Fiyat (EUR)", "city": "Sehir",
            "description": "Aciklama", "image": "Kapak gorseli", "delivery": "Teslimat",
            "free_shipping": "Ucretsiz kargo", "is_active": "Yayinda", "track_stock": "Stok takibi",
            "stock": "Stok adedi",
        }

    def __init__(self, *args, shop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.shop = shop or self.instance.shop
        self.fields["category"].queryset = Category.objects.filter(
            mode=Mode.SHOP, parent__isnull=False
        ).select_related("parent")
        self.fields["category"].label_from_instance = (
            lambda obj: f"{obj.parent.name('tr')} › {obj.name('tr')}"
        )
        self.fields["city"].queryset = City.objects.filter(country=self.shop.country)
        self.fields["city"].required = False

    def save(self, commit=True):
        item = super().save(commit=False)
        item.mode = Mode.SHOP
        item.shop = self.shop
        item.country = self.shop.country
        item.condition = "new"
        root = item.category.parent or item.category
        item.icon = root.icon
        item.hue = self.shop.hue
        if commit:
            item.save()
        return item


class ListingImageForm(forms.ModelForm):
    class Meta:
        model = ListingImage
        fields = ("image",)


ListingImageFormSet = forms.modelformset_factory(
    ListingImage, form=ListingImageForm, extra=49, max_num=49, validate_max=True, can_delete=True
)


class IndividualListingForm(VideoCleanMixin, forms.ModelForm):
    """Bireysel (ikinci el) ilan formu — sahibinden mantiginda."""

    class Meta:
        model = Listing
        fields = ("title", "category", "price_eur", "city", "condition", "delivery",
                  "description", "image", "video", "seller_phone")
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, country=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.country = country or self.instance.country
        self.fields["category"].queryset = Category.objects.filter(
            mode=Mode.USED, parent__isnull=False
        ).select_related("parent")
        self.fields["category"].label_from_instance = (
            lambda obj: f"{obj.parent.name('tr')} › {obj.name('tr')}"
        )
        self.fields["city"].queryset = City.objects.filter(country=self.country)
        self.fields["city"].required = False

    def save(self, commit=True, owner=None):
        item = super().save(commit=False)
        item.mode = Mode.USED
        item.country = self.country
        item.owner = owner or item.owner
        item.seller_name = owner.get_full_name() or owner.username if owner else item.seller_name
        root = item.category.parent or item.category
        item.icon = root.icon
        item.hue = item.hue or 190
        if commit:
            item.save()
        return item


class VariantForm(forms.ModelForm):
    class Meta:
        model = ListingVariant
        fields = ("name", "price_delta_eur", "stock", "sku")


VariantFormSet = forms.modelformset_factory(
    ListingVariant, form=VariantForm, extra=3, can_delete=True
)


class ReviewForm(forms.Form):
    rating = forms.ChoiceField(choices=[(i, f"{i} ★") for i in range(5, 0, -1)])
    comment = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)


class CouponForm(forms.Form):
    code = forms.CharField(max_length=30, required=False)


class ShipmentForm(forms.Form):
    carrier = forms.CharField(max_length=60, required=False)
    tracking_number = forms.CharField(max_length=80, required=False)


def photo_count_error(form, formset):
    """Kapak dahil toplam fotograf sayisi MIN/MAX araligi disindaysa hata metni dondurur."""
    n = 1 if form.cleaned_data.get("image") else 0
    for f in formset.forms:
        cd = getattr(f, "cleaned_data", None) or {}
        if cd and not cd.get("DELETE") and cd.get("image"):
            n += 1
    lo, hi = settings.MIN_LISTING_IMAGES, settings.MAX_LISTING_IMAGES
    if n < lo:
        return f"En az {lo} fotograf yuklemelisin (kapak dahil, su an {n})."
    if n > hi:
        return f"En fazla {hi} fotograf yukleyebilirsin (su an {n})."
    return None
