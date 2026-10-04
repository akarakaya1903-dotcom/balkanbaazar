from django.db.models import F
from django.utils import timezone

SKIP_PREFIXES = ("/admin", "/yonetim", "/static", "/media", "/r/", "/odeme/webhook", "/sitemap", "/robots", "/favicon")
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
