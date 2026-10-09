# -*- coding: utf-8 -*-
"""Uyelik, magaza basvurusu ve satici paneli."""
from django.contrib import messages
from django.contrib.auth import get_user_model, login, views as auth_views
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render

from django.utils import timezone

from . import emails
from .i18n import msg
from .forms import (ListingImageFormSet, photo_count_error, ProductForm, ShipmentForm,
                    ShopApplicationForm, ShopSettingsForm, SignUpForm, VariantFormSet)
from .models import (ApplicationStatus, Listing, ListingImage, ListingVariant,
                     OrderItem, Shop, ShopApplication)


def signup(request):
    if request.user.is_authenticated:
        return redirect("market:panel")
    from . import antispam
    if request.method == "POST" and antispam.looks_like_bot(request):
        messages.error(request, msg(request, "m_form_fail"))
        return redirect("market:signup")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        emails.notify_staff_new_user(user)
        emails.welcome_user(user, emails.lang_of(request))
        from .tracking import bb_event
        bb_event(request, "CompleteRegistration", {"status": True})
        emails.send_verification(user, emails.lang_of(request))
        messages.success(request, msg(request, "m_acct_ready"))
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
        # Magaza yonetici onayina kadar acilmaz (Shop kaydi onayda olusur).
        from .tracking import bb_event
        bb_event(request, "SubmitApplication")
        emails.notify_application_received(application, emails.lang_of(request))
        emails.notify_staff_new_application(application)
        messages.success(request, msg(request, "apply_received"))
        return render(request, "market/account/apply_done.html", {"application": application})
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
    photo_err = None
    if request.method == "POST" and form.is_valid() and formset.is_valid() and variant_formset.is_valid():
        photo_err = photo_count_error(form, formset)
        if photo_err:
            messages.error(request, photo_err)
    if request.method == "POST" and photo_err is None and form.is_valid() and formset.is_valid() and variant_formset.is_valid():
        saved_item = form.save()
        if not item:
            # Yeni urun yonetici onayina kadar yayinlanmaz.
            saved_item.is_active = False
            saved_item.pending_review = True
            saved_item.save(update_fields=["is_active", "pending_review"])
            emails.notify_staff_pending_listing(saved_item)
            emails.notify_listing_received(saved_item, emails.lang_of(request))
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
        messages.success(request, msg(request, "product_pending") if not item else msg(request, "m_product_saved"))
        from .videos import start_video_job
        start_video_job(saved_item)
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
        messages.success(request, msg(request, "m_product_deleted"))
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
        messages.success(request, msg(request, "m_shop_updated"))
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
            messages.success(request, msg(request, "m_ship_saved"))
    return redirect("market:panel_orders")


@login_required
def profile(request):
    from django import forms
    from django.contrib.auth import get_user_model

    class ProfileForm(forms.ModelForm):
        class Meta:
            model = get_user_model()
            fields = ["first_name", "last_name", "email"]

    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, msg(request, "m_profile_updated"))
        return redirect("market:profile")
    from .models import email_is_verified
    return render(request, "market/account/profile.html", {"form": form, "verified": email_is_verified(request.user)})


class PwResetConfirm(auth_views.PasswordResetConfirmView):
    """Sifre sifirlama tamamlaninca kullaniciya bilgi e-postasi gonderir."""
    template_name = "market/account/pw_confirm.html"
    success_url = reverse_lazy("market:password_reset_complete")

    def form_valid(self, form):
        response = super().form_valid(form)
        emails.notify_password_changed(form.user)
        return response


class PwChange(auth_views.PasswordChangeView):
    template_name = "market/account/pw_change.html"
    success_url = reverse_lazy("market:profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        emails.notify_password_changed(self.request.user)
        messages.success(self.request, msg(self.request, "m_pw_changed"))
        return response


@login_required
def delete_account(request):
    """Hesabi anonimlestirip kapatir. Siparis gecmisi satici icin korunur, kisisel veriler silinir."""
    user = request.user
    if Shop.objects.filter(owner=user).exists():
        messages.error(request, msg(request, "m_shop_owner_delete"))
        return redirect("market:profile")
    if request.method == "POST":
        has_pw = user.has_usable_password()
        ok = (user.check_password(request.POST.get("password", "")) if has_pw
              else request.POST.get("confirm", "").strip().lower() == (user.email or "").lower())
        if not ok:
            messages.error(request, msg(request, "m_verify_failed"))
            return redirect("market:delete_account")
        Listing.objects.filter(owner=user).update(is_active=False, seller_name="", seller_phone="")
        uid = user.pk
        user.username = f"silinen-{uid}"
        user.email = ""
        user.first_name = ""
        user.last_name = ""
        user.is_active = False
        user.set_unusable_password()
        user.save()
        from django.contrib.auth import logout
        logout(request)
        messages.success(request, msg(request, "m_acct_deleted"))
        return redirect("market:home")
    return render(request, "market/account/delete_account.html", {"has_pw": user.has_usable_password()})


def verify_email(request, token):
    from django.core import signing
    from .models import UserProfile
    try:
        data = signing.loads(token, salt="bb-verify", max_age=3 * 86400)
        user = get_user_model().objects.get(pk=data["u"], email=data["e"])
    except Exception:
        messages.error(request, msg(request, "m_verify_link_bad"))
        return redirect("market:profile" if request.user.is_authenticated else "market:login")
    prof, _ = UserProfile.objects.get_or_create(user=user)
    prof.email_verified = True
    prof.save(update_fields=["email_verified"])
    messages.success(request, msg(request, "m_email_verified"))
    return redirect("market:profile" if request.user.is_authenticated else "market:login")


@login_required
def resend_verification(request):
    if request.method == "POST":
        emails.send_verification(request.user, emails.lang_of(request))
        messages.success(request, msg(request, "m_verify_sent"))
    return redirect("market:profile")


@login_required
def panel_verification(request):
    import os
    from .models import VerificationRequest
    shop = _owned_shop(request)
    if not shop:
        return redirect("market:shop_apply")
    pending = shop.verification_requests.filter(status="pending").first()
    if request.method == "POST" and not shop.verified and not pending:
        doc = request.FILES.get("document")
        ext = os.path.splitext(doc.name)[1].lower() if doc else ""
        if not doc or ext not in (".pdf", ".jpg", ".jpeg", ".png"):
            messages.error(request, msg(request, "m_doc_type"))
        elif doc.size > 8 * 1024 * 1024:
            messages.error(request, msg(request, "m_doc_size"))
        else:
            vr = VerificationRequest.objects.create(shop=shop, document=doc, note=request.POST.get("note", "")[:500])
            emails.notify_staff_verification(vr)
            messages.success(request, msg(request, "m_verif_received"))
            return redirect("market:panel_verification")
    return render(request, "market/panel/verification.html", {
        "shop": shop, "pending": pending, "last": shop.verification_requests.first()})
