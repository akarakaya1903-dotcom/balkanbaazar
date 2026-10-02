# -*- coding: utf-8 -*-
"""Uyelik, magaza basvurusu ve satici paneli."""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from django.utils import timezone

from . import emails
from .forms import (ListingImageFormSet, ProductForm, ShipmentForm,
                    ShopApplicationForm, ShopSettingsForm, SignUpForm, VariantFormSet)
from .models import (ApplicationStatus, Listing, ListingImage, ListingVariant,
                     OrderItem, Shop, ShopApplication)


def signup(request):
    if request.user.is_authenticated:
        return redirect("market:panel")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Hesabin hazir.")
        return redirect("market:panel")
    return render(request, "market/account/signup.html", {"form": form})


@login_required
def shop_apply(request):
    """Magaza basvuru formu. Zaten magazasi olan panele gider."""
    shop = Shop.objects.filter(owner=request.user).first()
    if shop:
        return redirect("market:panel")
    pending = ShopApplication.objects.filter(
        applicant=request.user, status=ApplicationStatus.PENDING
    ).first()
    if pending:
        return render(request, "market/account/apply_done.html", {"application": pending})

    initial = {"contact_name": request.user.get_full_name() or request.user.username,
               "email": request.user.email}
    form = ShopApplicationForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        application = form.save(commit=False)
        application.applicant = request.user
        application.save()
        # Magaza aninda acilir; firma hemen urun ekleyebilir.
        shop = application.approve()
        emails.notify_application_approved(application, shop)
        emails.notify_staff_new_application(application)
        messages.success(request, "Magazan acildi. Ilk urununu ekleyebilirsin.")
        return redirect("market:panel_product_new")
    return render(request, "market/account/apply.html", {"form": form})


def _owned_shop(request):
    return Shop.objects.filter(owner=request.user).select_related("country", "city").first()


@login_required
def panel(request):
    shop = _owned_shop(request)
    application = ShopApplication.objects.filter(applicant=request.user).first()
    if not shop:
        return render(request, "market/panel/no_shop.html", {"application": application})
    items = shop.listings.all()
    ctx = {
        "shop": shop,
        "product_count": items.count(),
        "active_count": items.filter(is_active=True).count(),
        "total_views": items.aggregate(n=Sum("views"))["n"] or 0,
        "total_favs": items.aggregate(n=Sum("favorites"))["n"] or 0,
        "recent": items[:8],
    }
    return render(request, "market/panel/dashboard.html", ctx)


@login_required
def panel_products(request):
    shop = _owned_shop(request)
    if not shop:
        return redirect("market:shop_apply")
    return render(request, "market/panel/products.html",
                  {"shop": shop, "items": shop.listings.all()})


@login_required
def panel_product_form(request, pk=None):
    shop = _owned_shop(request)
    if not shop:
        return redirect("market:shop_apply")
    item = get_object_or_404(Listing, pk=pk, shop=shop) if pk else None
    form = ProductForm(
        request.POST or None, request.FILES or None, instance=item, shop=shop
    )
    gallery_qs = ListingImage.objects.filter(listing=item) if item else ListingImage.objects.none()
    formset = ListingImageFormSet(
        request.POST or None, request.FILES or None, queryset=gallery_qs, prefix="gallery"
    )
    variant_qs = ListingVariant.objects.filter(listing=item) if item else ListingVariant.objects.none()
    variant_formset = VariantFormSet(request.POST or None, queryset=variant_qs, prefix="variant")
    if request.method == "POST" and form.is_valid() and formset.is_valid() and variant_formset.is_valid():
        saved_item = form.save()
        images = formset.save(commit=False)
        for img in images:
            img.listing = saved_item
            img.save()
        for obj in formset.deleted_objects:
            obj.delete()
        variants = variant_formset.save(commit=False)
        for v in variants:
            v.listing = saved_item
            v.save()
        for obj in variant_formset.deleted_objects:
            obj.delete()
        messages.success(request, "Urun kaydedildi.")
        return redirect("market:panel_products")
    return render(request, "market/panel/product_form.html",
                  {"form": form, "shop": shop, "item": item, "formset": formset,
                   "variant_formset": variant_formset})


@login_required
def panel_product_delete(request, pk):
    shop = _owned_shop(request)
    item = get_object_or_404(Listing, pk=pk, shop=shop)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Urun silindi.")
        return redirect("market:panel_products")
    return render(request, "market/panel/product_delete.html", {"item": item, "shop": shop})


@login_required
def panel_settings(request):
    shop = _owned_shop(request)
    if not shop:
        return redirect("market:shop_apply")
    form = ShopSettingsForm(request.POST or None, instance=shop)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Magaza bilgileri guncellendi.")
        return redirect("market:panel_settings")
    return render(request, "market/panel/settings.html", {"form": form, "shop": shop})


@login_required
def panel_billing(request):
    shop = _owned_shop(request)
    if not shop:
        return redirect("market:shop_apply")
    return render(request, "market/panel/billing.html", {"shop": shop})


@login_required
def panel_orders(request):
    shop = _owned_shop(request)
    if not shop:
        return redirect("market:shop_apply")
    items = (OrderItem.objects.filter(shop=shop)
             .select_related("order", "order__buyer", "listing", "variant")
             .order_by("-order__created_at"))
    return render(request, "market/panel/orders.html", {"shop": shop, "items": items})


@login_required
def panel_order_ship(request, item_id):
    shop = _owned_shop(request)
    item = get_object_or_404(OrderItem, pk=item_id, shop=shop)
    if request.method == "POST":
        form = ShipmentForm(request.POST)
        if form.is_valid():
            item.carrier = form.cleaned_data["carrier"]
            item.tracking_number = form.cleaned_data["tracking_number"]
            item.shipped_at = timezone.now()
            item.save(update_fields=["carrier", "tracking_number", "shipped_at"])
            emails.notify_order_shipped(item)
            messages.success(request, "Kargo bilgisi kaydedildi.")
    return redirect("market:panel_orders")
