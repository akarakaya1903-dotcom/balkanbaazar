from django.db.models import F
from django.utils import timezone

SKIP_PREFIXES = ("/admin", "/yonetim", "/static", "/media", "/r/", "/odeme/webhook", "/sitemap", "/robots", "/favicon", "/saglik")
BOT_WORDS = ("bot", "crawl", "spider", "slurp", "facebookexternalhit", "preview", "monitor")


class VisitorCounterMiddleware:
    """Cerezle gunde bir kez tekil ziyaretci sayar. Hata olursa siteyi bozmaz."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            ctype = response.get("Content-Type", "")
            ua = request.META.get("HTTP_USER_AGENT", "").lower()
            if (request.method == "GET" and response.status_code == 200 and "text/html" in ctype
                    and not request.path.startswith(SKIP_PREFIXES)
                    and not any(w in ua for w in BOT_WORDS)):
                from .models import DailyStat
                today = timezone.localdate()
                stat, _ = DailyStat.objects.get_or_create(day=today)
                fields = {"pageviews": F("pageviews") + 1}
                if request.COOKIES.get("bb_v") != str(today):
                    fields["visitors"] = F("visitors") + 1
                    response.set_cookie("bb_v", str(today), max_age=86400, samesite="Lax",
                                        secure=request.is_secure())
                DailyStat.objects.filter(pk=stat.pk).update(**fields)
        except Exception:
            pass
        return response


class ThrottleMiddleware:
    """Giris/kayit/sifre sifirlama POST'larinda IP basina hiz siniri (kaba kuvvet ve sahte kayit onlemi)."""
    LIMIT = 15
    WINDOW = 300  # saniye

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith(("/uyelik/", "/admin/login")):
            from django.core.cache import cache
            from django.http import HttpResponse
            ip = request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR", "")
            key = f"throttle:{ip}"
            cache.add(key, 0, self.WINDOW)
            try:
                n = cache.incr(key)
            except ValueError:
                n = 1
            if n > self.LIMIT:
                return HttpResponse("Cok fazla deneme. Lutfen birkac dakika sonra tekrar dene.", status=429)
        return self.get_response(request)


class StaffTwoFactorMiddleware:
    """Yonetici (staff) hesaplari /admin/ ve /yonetim/ alanina girmeden once iki adimli kodu girmek zorundadir.
    Acil durumda kapatmak icin ortam degiskeni: STAFF_2FA_DISABLED=1"""
    GUARDED = ("/admin/", "/yonetim/", "/dogrulama-belge/")
    EXEMPT = ("/admin/login/", "/admin/logout/", "/admin/jsi18n/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings
        path = request.path_info
        if (not settings.STAFF_2FA_DISABLED and path.startswith(self.GUARDED)
                and not path.startswith(self.EXEMPT)):
            user = getattr(request, "user", None)
            if (user is not None and user.is_authenticated and user.is_staff
                    and request.session.get("bb_2fa_user") != user.pk):
                from urllib.parse import quote
                from django.http import HttpResponseRedirect
                return HttpResponseRedirect("/uyelik/iki-adim/?next=" + quote(request.get_full_path()))
        return self.get_response(request)


class LanguagePrefixMiddleware:
    """/mk/..., /sq/... gibi dil onekli adresleri ayni sayfalara baglar ve dili o adresten alir.
    {% url %} baglantilari betik oneki sayesinde otomatik olarak dil onekiyle uretilir."""

    def __init__(self, get_response):
        import re
        from .i18n import T
        self.get_response = get_response
        self.pattern = re.compile(r"^/(" + "|".join(sorted(T.keys())) + r")(/.*)?$")

    def __call__(self, request):
        m = self.pattern.match(request.path_info)
        if not m:
            return self.get_response(request)
        from django.conf import settings
        from django.http import HttpResponseRedirect
        from django.urls import get_script_prefix, set_script_prefix
        lang, rest = m.group(1), m.group(2)
        if not rest:
            return HttpResponseRedirect(f"/{lang}/")
        original = get_script_prefix()
        request.lang_override = lang
        request.path_info = rest
        if request.COOKIES.get(settings.SESSION_COOKIE_NAME) and request.session.get("lang") != lang:
            request.session["lang"] = lang
        set_script_prefix(original.rstrip("/") + f"/{lang}/")
        try:
            return self.get_response(request)
        finally:
            set_script_prefix(original)
