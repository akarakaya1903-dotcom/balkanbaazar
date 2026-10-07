# -*- coding: utf-8 -*-
"""Ozel yonetim paneli — site sahibinin kendi arayuzu (Django admin degil).

Erisim sadece is_staff=True kullanicilara acik. Superuser olusturulunca
(is_staff otomatik True olur) buraya /yonetim/ adresinden girilir.
"""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import emails
from .models import (ApplicationStatus, Country, Listing, Mode, Shop,
                     ShopApplication, ShopPlan)


def _denied(request):
    return render(request, "market/staff/denied.html", status=403)


def staff_gate(view):
    """login gerektirir; giris yapan ama staff olmayana nazik bir mesaj gosterir."""
    @login_required
    def wrapped(request, *a, **kw):
        if not request.user.is_staff:
            return _denied(request)
        return view(request, *a, **kw)
    return wrapped


@staff_gate
def dashboard(request):
    week_ago = timezone.now() - timezone.timedelta(days=7)
    ctx = {
        "pending_count": ShopApplication.objects.filter(status=ApplicationStatus.PENDING).count(),
        "shop_count": Shop.objects.count(),
        "listing_count": Listing.objects.count(),
        "user_count": Shop.objects.values("owner").distinct().count(),
        "recent_apps": ShopApplication.objects.filter(status=ApplicationStatus.PENDING)
                       .select_related("country", "applicant")[:6],
        "recent_shops": Shop.objects.select_related("country", "owner").order_by("-opened_at")[:6],
        "new_this_week": ShopApplication.objects.filter(created_at__gte=week_ago).count(),
    }
    ctx["stf"] = "dash"
    return render(request, "market/staff/dashboard.html", ctx)


@staff_gate
def applications(request):
    status = request.GET.get("status", ApplicationStatus.PENDING)
    qs = ShopApplication.objects.select_related("country", "applicant", "category")
    if status in {ApplicationStatus.PENDING, ApplicationStatus.APPROVED, ApplicationStatus.REJECTED}:
        qs = qs.filter(status=status)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(shop_name__icontains=q)
    page = Paginator(qs, 20).get_page(request.GET.get("page"))
    return render(request, "market/staff/applications.html",
                  {"page_obj": page, "status": status, "q": q, "stf": "apps",
                   "counts": {
                       "pending": ShopApplication.objects.filter(status=ApplicationStatus.PENDING).count(),
                       "approved": ShopApplication.objects.filter(status=ApplicationStatus.APPROVED).count(),
                       "rejected": ShopApplication.objects.filter(status=ApplicationStatus.REJECTED).count(),
                   }})


@staff_gate
@require_POST
def application_approve(request, pk):
    application = get_object_or_404(ShopApplication, pk=pk, status=ApplicationStatus.PENDING)
    shop = application.approve()
    emails.notify_application_approved(application, shop)
    messages.success(request, f"{shop.name} onaylandı ve açıldı (ilk 3 ay ücretsiz).")
    return redirect(request.POST.get("next") or "market:staff_applications")


@staff_gate
@require_POST
def application_reject(request, pk):
    application = get_object_or_404(ShopApplication, pk=pk, status=ApplicationStatus.PENDING)
    application.status = ApplicationStatus.REJECTED
    application.staff_note = request.POST.get("note", "")
    application.save(update_fields=["status", "staff_note"])
    emails.notify_application_rejected(application)
    messages.success(request, f"{application.shop_name} başvurusu reddedildi.")
    return redirect(request.POST.get("next") or "market:staff_applications")


@staff_gate
def shops(request):
    qs = Shop.objects.select_related("country", "city", "owner").annotate(
        n_listings=Count("listings")
    )
    country = request.GET.get("country", "")
    if country:
        qs = qs.filter(country__code=country)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(name__icontains=q)
    page = Paginator(qs, 24).get_page(request.GET.get("page"))
    return render(request, "market/staff/shops.html",
                  {"page_obj": page, "countries": Country.objects.all(), "country": country,
                   "q": q, "stf": "shops"})


@staff_gate
@require_POST
def shop_toggle_verified(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    shop.verified = not shop.verified
    shop.save(update_fields=["verified"])
    return redirect(request.POST.get("next") or "market:staff_shops")


@staff_gate
@require_POST
def shop_set_plan(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    plan = request.POST.get("plan")
    if plan in ShopPlan.values:
        shop.plan = plan
        shop.save(update_fields=["plan"])
        messages.success(request, f"{shop.name} paketi güncellendi.")
    return redirect(request.POST.get("next") or "market:staff_shops")


@staff_gate
def listings(request):
    qs = Listing.objects.select_related("country", "category", "shop")
    mode = request.GET.get("mode", "")
    if mode in {Mode.USED, Mode.SHOP}:
        qs = qs.filter(mode=mode)
    country = request.GET.get("country", "")
    if country:
        qs = qs.filter(country__code=country)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(title__icontains=q)
    page = Paginator(qs.order_by("-created_at"), 24).get_page(request.GET.get("page"))
    return render(request, "market/staff/listings.html",
                  {"page_obj": page, "countries": Country.objects.all(),
                   "mode": mode, "country": country, "q": q, "stf": "listings"})


@staff_gate
@require_POST
def listing_toggle_active(request, pk):
    item = get_object_or_404(Listing, pk=pk)
    item.is_active = not item.is_active
    if item.is_active:
        item.pending_review = False  # yonetici acarsa onaylanmis sayilir
    item.save(update_fields=["is_active", "pending_review"])
    return redirect(request.POST.get("next") or "market:staff_listings")


@staff_gate
@require_POST
def listing_delete(request, pk):
    item = get_object_or_404(Listing, pk=pk)
    item.delete()
    messages.success(request, "İlan silindi.")
    return redirect(request.POST.get("next") or "market:staff_listings")


@staff_gate
def countries(request):
    if request.method == "POST":
        for country in Country.objects.all():
            raw = request.POST.get(f"rate_{country.code}")
            if raw:
                try:
                    country.rate_per_eur = float(raw.replace(",", "."))
                    country.save(update_fields=["rate_per_eur"])
                except ValueError:
                    pass
        messages.success(request, "Kurlar güncellendi.")
        return redirect("market:staff_countries")
    return render(request, "market/staff/countries.html",
                  {"countries": Country.objects.annotate(
                      n_shops=Count("shops", distinct=True),
                      n_listings=Count("listings", distinct=True),
                  ), "stf": "countries"})
