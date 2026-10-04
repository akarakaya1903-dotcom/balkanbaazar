from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.views.static import serve

from market.sitemaps import ListingSitemap, PageSitemap, ShopSitemap, StaticSitemap

SITEMAPS = {"static": StaticSitemap, "listings": ListingSitemap, "shops": ShopSitemap, "pages": PageSitemap}


def robots(request):
    body = ("User-agent: *\nDisallow: /admin/\nDisallow: /yonetim/\nDisallow: /panel/\nDisallow: /sepet/\nDisallow: /odeme/\nDisallow: /uyelik/\n"
            "Sitemap: https://balkanbaazar.com/sitemap.xml\n")
    return HttpResponse(body, content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", robots, name="robots"),
    path("", include("market.urls")),
    # Yuklenen gorseller (urun, logo, banner). Kucuk/orta siteler icin yeterli;
    # buyuyunce bulut depolamaya (S3, Cloudinary) gecmek daha iyi olur.
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
