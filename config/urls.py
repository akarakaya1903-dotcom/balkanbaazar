from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.views.static import serve

from market.sitemaps import ListingSitemap, PageSitemap, ShopSitemap, StaticSitemap

SITEMAPS = {"static": StaticSitemap, "listings": ListingSitemap, "shops": ShopSitemap, "pages": PageSitemap}


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
    js = "self.addEventListener('install',function(){self.skipWaiting();});self.addEventListener('activate',function(e){e.waitUntil(self.clients.claim());});self.addEventListener('fetch',function(){});"
    resp = HttpResponse(js, content_type="application/javascript")
    resp["Cache-Control"] = "no-cache"
    return resp


def favicon(request):
    from django.http import FileResponse
    return FileResponse(open(settings.BASE_DIR / "static" / "img" / "favicon.ico", "rb"), content_type="image/x-icon")


def robots(request):
    body = ("User-agent: *\nDisallow: /admin/\nDisallow: /yonetim/\nDisallow: /panel/\nDisallow: /sepet/\nDisallow: /odeme/\nDisallow: /uyelik/\n"
            "Sitemap: https://balkanbaazar.com/sitemap.xml\n")
    return HttpResponse(body, content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", robots, name="robots"),
    path("manifest.webmanifest", manifest, name="manifest"),
    path("sw.js", service_worker, name="sw"),
    path("favicon.ico", favicon, name="favicon"),
    path("", include("market.urls")),
    # Yuklenen gorseller (urun, logo, banner). Kucuk/orta siteler icin yeterli;
    # buyuyunce bulut depolamaya (S3, Cloudinary) gecmek daha iyi olur.
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
