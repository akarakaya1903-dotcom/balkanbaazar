from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.contrib.sitemaps.views import index, sitemap
from django.http import HttpResponse
from django.views.static import serve

from market.sitemaps import CategorySitemap, ListingSitemap, PageSitemap, ShopSitemap, StaticSitemap, expand

SITEMAPS = {"static": expand(StaticSitemap), "categories": expand(CategorySitemap), "listings": expand(ListingSitemap), "shops": expand(ShopSitemap), "pages": expand(PageSitemap)}


def manifest(request):
    import json
    from django.templatetags.static import static
    data = {"name": "Balkan Baazar", "short_name": "Balkan Baazar", "start_url": "/", "scope": "/",
            "display": "standalone", "background_color": "#0D2A3A", "theme_color": "#0D2A3A",
            "description": "Balkanlarin yeni pazaryeri",
            "icons": [{"src": static("img/logo-192.png"), "sizes": "192x192", "type": "image/png", "purpose": "any"},
                      {"src": static("img/logo-512.png"), "sizes": "512x512", "type": "image/png", "purpose": "any"}]}
    return HttpResponse(json.dumps(data), content_type="application/manifest+json")


def service_worker(request):
    js = "self.addEventListener('install',function(){self.skipWaiting();});self.addEventListener('activate',function(e){e.waitUntil(self.clients.claim());});self.addEventListener('fetch',function(){});self.addEventListener('push',function(e){var d={};try{d=e.data.json();}catch(x){}e.waitUntil(self.registration.showNotification(d.title||'Balkan Baazar',{body:d.body||'',icon:'/static/img/logo-192.png',badge:'/static/img/logo-96.png',tag:d.tag||'bb',renotify:true,data:{url:d.url||'/'}}));});self.addEventListener('notificationclick',function(e){e.notification.close();var u=(e.notification.data&&e.notification.data.url)||'/';e.waitUntil(clients.matchAll({type:'window',includeUncontrolled:true}).then(function(l){for(var i=0;i<l.length;i++){if('focus' in l[i]){l[i].navigate(u);return l[i].focus();}}return clients.openWindow(u);}));});"
    resp = HttpResponse(js, content_type="application/javascript")
    resp["Cache-Control"] = "no-cache"
    return resp


def favicon(request):
    from django.http import FileResponse
    return FileResponse(open(settings.BASE_DIR / "static" / "img" / "favicon.ico", "rb"), content_type="image/x-icon")


def robots(request):
    from market.i18n import T
    private = ["/admin/", "/yonetim/", "/panel/", "/sepet/", "/odeme/", "/uyelik/"]
    lines = ["User-agent: *"]
    for prefix in [""] + ["/" + c for c in T.keys()]:
        lines += [f"Disallow: {prefix}{path}" for path in private]
    lines.append("Sitemap: https://balkanbaazar.com/sitemap.xml")
    body = "\n".join(lines) + "\n"
    return HttpResponse(body, content_type="text/plain")


def health(request):
    """Calisma kontrolu (UptimeRobot vb. icin): veritabani yanitliyorsa 200, degilse 503."""
    from django.db import connection
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
    except Exception:
        return HttpResponse("db-error", status=503, content_type="text/plain")
    resp = HttpResponse("ok", content_type="text/plain")
    resp["Cache-Control"] = "no-store"
    return resp


urlpatterns = [
    path("saglik/", health, name="health"),
    path("admin/", admin.site.urls),
    path("sitemap.xml", index, {"sitemaps": SITEMAPS}),
    path("sitemap-<section>.xml", sitemap, {"sitemaps": SITEMAPS}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", robots, name="robots"),
    path("manifest.webmanifest", manifest, name="manifest"),
    path("sw.js", service_worker, name="sw"),
    path("favicon.ico", favicon, name="favicon"),
    path("", include("market.urls")),
    # Yuklenen gorseller (urun, logo, banner). Kucuk/orta siteler icin yeterli;
    # buyuyunce bulut depolamaya (S3, Cloudinary) gecmek daha iyi olur.
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
