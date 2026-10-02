from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("market.urls")),
    # Yuklenen gorseller (urun, logo, banner). Kucuk/orta siteler icin yeterli;
    # buyuyunce bulut depolamaya (S3, Cloudinary) gecmek daha iyi olur.
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
