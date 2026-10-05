from django.contrib import admin

from .models import (ApplicationStatus, Boost, Category, City, Conversation, Coupon,
                     Country, Favorite, Listing, ListingImage, ListingVariant, Message,
                     Order, OrderItem, Review, Shop, ShopApplication, SiteSettings, Banner, Page, DailyStat, ListingReport)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("flag", "code", "name_local", "name_tr", "currency", "rate_per_eur", "is_active")
    list_editable = ("rate_per_eur", "is_active")


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    list_filter = ("country",)
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "mode", "parent", "slug", "order")
    list_filter = ("mode", "parent")
    search_fields = ("slug",)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "country", "city", "plan", "verified", "product_count")
    list_filter = ("country", "plan", "verified")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


class ListingVariantInline(admin.TabularInline):
    model = ListingVariant
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "mode", "country", "city", "price_eur", "category", "shop",
                    "is_active", "pending_review", "track_stock", "stock", "featured_until")
    list_filter = ("pending_review", "mode", "country", "condition", "delivery", "is_active", "track_stock")
    actions = ["approve_listings"]
    search_fields = ("title", "description")
    autocomplete_fields = ("city",)
    inlines = [ListingImageInline, ListingVariantInline]

    @admin.action(description="Secili ilanlari onayla ve yayinla")
    def approve_listings(self, request, queryset):
        n = queryset.update(is_active=True, pending_review=False)
        self.message_user(request, f"{n} ilan yayinlandi.")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "shop", "percent_off", "amount_off_eur", "active", "used_count", "max_uses", "valid_until")
    list_filter = ("active",)
    search_fields = ("code",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "shop", "created_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("listing", "author", "rating", "created_at")
    list_filter = ("rating",)


@admin.register(ShopApplication)
class ShopApplicationAdmin(admin.ModelAdmin):
    list_display = ("shop_name", "applicant", "country", "status", "created_at", "shop")
    list_filter = ("status", "country")
    search_fields = ("shop_name", "contact_name", "email")
    readonly_fields = ("created_at", "shop")
    actions = ("approve_selected", "reject_selected")

    @admin.action(description="Secili basvurulari onayla ve magazayi ac")
    def approve_selected(self, request, queryset):
        created = 0
        for application in queryset.filter(status=ApplicationStatus.PENDING):
            application.approve()
            created += 1
        self.message_user(request, f"{created} magaza acildi (ilk 3 ay ucretsiz).")

    @admin.action(description="Secili basvurulari reddet")
    def reject_selected(self, request, queryset):
        updated = queryset.filter(status=ApplicationStatus.PENDING).update(
            status=ApplicationStatus.REJECTED
        )
        self.message_user(request, f"{updated} basvuru reddedildi.")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("listing", "shop", "title", "price_eur", "qty")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "country", "status", "total_eur", "paid_at", "created_at")
    list_filter = ("status", "country")
    readonly_fields = ("stripe_session_id", "paid_at")
    inlines = [OrderItemInline]


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "body", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "participant_a", "participant_b", "updated_at")
    inlines = [MessageInline]


@admin.register(Boost)
class BoostAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "buyer", "days", "price_eur", "status", "paid_at")
    list_filter = ("status",)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Sadece bir kayit olur; banner gorseli buradan yuklenir."""
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "advertiser", "place", "order", "is_active", "starts_at", "ends_at", "clicks")
    list_editable = ("order", "is_active")
    list_filter = ("place", "is_active")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "group", "order", "is_published")
    list_editable = ("order", "is_published")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(DailyStat)
class DailyStatAdmin(admin.ModelAdmin):
    list_display = ("day", "visitors", "pageviews")
    readonly_fields = ("day", "visitors", "pageviews")

    def has_add_permission(self, request):
        return False


# ---- Yonetim paneli ana sayfasi: ozet kartlari ----
admin.site.site_title = "Balkan Baazar"
admin.site.index_title = "Genel bakis"
_orig_index = admin.site.index


def _dashboard_index(request, extra_context=None):
    from django.contrib.auth import get_user_model
    from django.urls import reverse
    from django.utils import timezone
    from .models import Order, ShopApplication
    today = timezone.localdate()
    stat = DailyStat.objects.filter(day=today).first()

    def link(name):
        try:
            return reverse(name)
        except Exception:
            return "#"
    User = get_user_model()
    stats = [
        {"label": "Bugunku ziyaretci", "value": stat.visitors if stat else 0, "url": link("admin:market_dailystat_changelist")},
        {"label": "Toplam uye", "value": User.objects.count(), "url": link("admin:auth_user_changelist")},
        {"label": "Bugun yeni uye", "value": User.objects.filter(date_joined__date=today).count(), "url": link("admin:auth_user_changelist")},
        {"label": "Aktif ilan", "value": Listing.objects.filter(is_active=True).count(), "url": link("admin:market_listing_changelist")},
        {"label": "Magaza", "value": Shop.objects.count(), "url": link("admin:market_shop_changelist")},
        {"label": "Bekleyen basvuru", "value": ShopApplication.objects.filter(status=ApplicationStatus.PENDING).count(), "url": link("admin:market_shopapplication_changelist")},
        {"label": "Bugunku siparis", "value": Order.objects.filter(created_at__date=today).count(), "url": link("admin:market_order_changelist")},
    ]
    context = {"bb_stats": stats}
    context.update(extra_context or {})
    return _orig_index(request, context)


admin.site.index = _dashboard_index


@admin.register(ListingReport)
class ListingReportAdmin(admin.ModelAdmin):
    list_display = ("listing", "reporter", "created_at", "resolved")
    list_editable = ("resolved",)
    list_filter = ("resolved",)
    readonly_fields = ("listing", "reporter", "message", "created_at")
