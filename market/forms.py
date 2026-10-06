from django.conf import settings
# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (Category, City, Listing, ListingImage, ListingVariant, Mode,
                     Shop, ShopApplication)


class CitySelect(forms.Select):
    """Sehir secenekleri icin ulke bilgisini (data-country) ekler; arama kutusu ulkeye gore daraltir."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        inst = getattr(value, "instance", None)
        if inst is not None:
            option["attrs"]["data-country"] = str(inst.country_id)
        return option


class CityAddMixin:
    """Aranabilir kategori/ulke/sehir kutulari + listede olmayan sehri yazarak ekleme (city_new)."""

    def _init_combo(self, depends=None):
        for name in ("category", "country"):
            if name in self.fields:
                self.fields[name].widget.attrs["data-combo"] = "1"
        c = self.fields["city"]
        attrs = {"data-combo": "1", "data-combo-add": "city_new"}
        if depends:
            attrs["data-depends"] = depends
        if self.is_bound and self.data.get("city_new"):
            attrs["data-new"] = self.data.get("city_new")
        c.widget = CitySelect(attrs=attrs)
        c.widget.choices = c.choices

    def clean(self):
        import re
        data = super().clean()
        new = " ".join((self.data.get("city_new") or "").split())[:60]
        if new and not data.get("city"):
            if not re.match(r"^[\w .'’()\-]{2,60}$", new):
                raise forms.ValidationError("Sehir adi gecersiz.")
            country = data.get("country") or getattr(self, "country", None) or getattr(getattr(self, "shop", None), "country", None)
            if country:
                existing = City.objects.filter(country=country, name__iexact=new).first()
                data["city"] = existing or City(country=country, name=new)
        return data

    def _persist_city(self, obj):
        city = getattr(obj, "city", None)
        if city is not None and city.pk is None:
            city.save()
            obj.city = city


class AttrFormMixin:
    """Kategoriye ozel alanlar (attr_*): kategoriye gore JS ile gosterilir, kayitta yalniz ilgili alanlar alinir."""

    def _init_attrs(self):
        import json
        from . import attributes as A
        for key, (kind, choices, cats) in A.all_keys().items():
            widget_attrs = {"data-cats": " ".join(cats)}
            if kind == "number":
                field = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(attrs=widget_attrs))
            elif kind == "select":
                field = forms.ChoiceField(required=False, widget=forms.Select(attrs=widget_attrs),
                                          choices=[("", "—")] + [(c, A.choice_label(c, "tr")) for c in choices])
            else:
                field = forms.CharField(required=False, max_length=60, widget=forms.TextInput(attrs=widget_attrs))
            field.label = A.label(key, "tr")
            self.fields["attr_" + key] = field
            self.initial["attr_" + key] = (self.instance.attrs or {}).get(key, "")
        self.cat_roots_json = json.dumps({c.pk: A.root_slug(c) for c in self.fields["category"].queryset})

    def collect_attrs(self, category):
        from . import attributes as A
        return A.clean_attrs(A.root_slug(category), self.cleaned_data)


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


class ShopApplicationForm(CityAddMixin, forms.ModelForm):
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
        self._init_combo(depends="id_country")

    def save(self, commit=True):
        obj = super().save(commit=False)
        self._persist_city(obj)
        if commit:
            obj.save()
        return obj


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


class ProductForm(CityAddMixin, AttrFormMixin, VideoCleanMixin, forms.ModelForm):
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
        self._init_attrs()
        self._init_combo()

    def save(self, commit=True):
        item = super().save(commit=False)
        item.mode = Mode.SHOP
        item.shop = self.shop
        item.country = self.shop.country
        item.condition = "new"
        item.attrs = self.collect_attrs(item.category)
        self._persist_city(item)
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


class IndividualListingForm(CityAddMixin, AttrFormMixin, VideoCleanMixin, forms.ModelForm):
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
        self._init_attrs()
        self._init_combo()

    def save(self, commit=True, owner=None):
        item = super().save(commit=False)
        item.mode = Mode.USED
        item.attrs = self.collect_attrs(item.category)
        self._persist_city(item)
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
