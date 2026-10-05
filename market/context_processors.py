from django.conf import settings

from .i18n import LANGUAGES, T
from .models import ApplicationStatus, Country, ShopApplication, SiteSettings, DailyStat, Message


def site_context(request):
    """Her sablonda ulke, dil ve metin sozlugu hazir olsun."""
    lang = request.session.get("lang", settings.DEFAULT_LANG)
    if lang not in T:
        lang = settings.DEFAULT_LANG
    countries = list(Country.objects.filter(is_active=True))
    code = request.session.get("country", settings.DEFAULT_COUNTRY)
    country = next((c for c in countries if c.code == code), countries[0] if countries else None)
    pending_badge = None
    cart_count = None
    unread_count = None
    if request.user.is_authenticated:
        if request.user.is_staff:
            n = ShopApplication.objects.filter(status=ApplicationStatus.PENDING).count()
            pending_badge = n or None
        cart = request.session.get("cart") or {}
        cart_count = sum(int(v) for v in cart.values()) or None
        from django.db.models import Q as _Q
        from .models import Conversation as _Conversation, Message as _Message
        convo_ids = _Conversation.objects.filter(
            _Q(participant_a=request.user) | _Q(participant_b=request.user)
        ).values_list("pk", flat=True)
        n_unread = _Message.objects.filter(conversation_id__in=convo_ids, is_read=False).exclude(
            sender=request.user
        ).count()
        unread_count = n_unread or None
    try:
        site_settings = SiteSettings.objects.first()
    except Exception:  # tablo henuz olusturulmadiysa (migrate oncesi) site yine acilsin
        site_settings = None
    try:
        from django.core.cache import cache
        from django.db.models import Sum
        from django.utils import timezone
        def _stats():
            today = DailyStat.objects.filter(day=timezone.localdate()).first()
            total = DailyStat.objects.aggregate(s=Sum("visitors"))["s"] or 0
            return {"today": today.visitors if today else 0, "total": total}
        visit_stats = cache.get_or_set("visit_stats", _stats, 60)
    except Exception:
        visit_stats = None
    fav_ids = set()
    try:
        if request.user.is_authenticated:
            from .models import Favorite
            fav_ids = set(Favorite.objects.filter(user=request.user, listing__isnull=False).values_list("listing_id", flat=True))
    except Exception:
        fav_ids = set()
    unread = 0
    try:
        u = request.user
        if u.is_authenticated:
            from django.db.models import Q
            unread = (Message.objects.filter(is_read=False)
                      .filter(Q(conversation__participant_a=u) | Q(conversation__participant_b=u))
                      .exclude(sender=u).count())
    except Exception:
        unread = 0
    from django.conf import settings as _s
    return {
        "unread_messages": unread,
        "fav_ids": fav_ids,
        "google_enabled": bool(_s.GOOGLE_CLIENT_ID),
        "min_images": _s.MIN_LISTING_IMAGES,
        "max_images": _s.MAX_LISTING_IMAGES,
        "visit_stats": visit_stats,
        "site_settings": site_settings,
        "t": T[lang],
        "pending_badge": pending_badge,
        "cart_count": cart_count,
        "unread_count": unread_count,
        "lang": lang,
        "languages": LANGUAGES,
        "countries": countries,
        "country": country,
        "site_name": settings.SITE_NAME,
        "mode": request.session.get("mode", "used"),
    }
