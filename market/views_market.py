# -*- coding: utf-8 -*-
"""Bireysel ilan verme, sepet/odeme, mesajlasma."""
import logging
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from . import emails
from .forms import (CouponForm, IndividualListingForm, ListingImageFormSet, ReviewForm,
                    photo_count_error)
from .models import (Boost, BoostStatus, Conversation, Coupon, Country, Favorite,
                     Listing, ListingImage, ListingVariant, Message, Mode, Order,
                     OrderItem, OrderStatus, Review, Shop)

log = logging.getLogger(__name__)

CART_KEY = "cart"  # session: {"<listing_id>": qty}


def _current_country(request):
    code = request.session.get("country", settings.DEFAULT_COUNTRY)
    return Country.objects.filter(code=code).first() or Country.objects.first()


# ---------------------------------------------------------------------------
# Bireysel ilan verme
# ---------------------------------------------------------------------------
@login_required
def my_listings(request):
    items = Listing.objects.filter(owner=request.user, mode=Mode.USED).select_related("category", "city")
    return render(request, "market/mylistings/list.html", {"items": items})


@login_required
def my_listing_form(request, pk=None):
    country = _current_country(request)
    item = get_object_or_404(Listing, pk=pk, owner=request.user) if pk else None
    from .models import email_is_verified
    if not pk and not email_is_verified(request.user):
        messages.error(request, "Ilan vermek icin once e-postani dogrulaman gerekiyor.")
        return redirect("market:profile")
    from . import antispam
    if request.method == "POST" and not pk and antispam.looks_like_bot(request):
        messages.error(request, "Form gonderilemedi, sayfayi yenileyip tekrar dene.")
        return redirect("market:my_listing_new")
    form = IndividualListingForm(
        request.POST or None, request.FILES or None, instance=item, country=country
    )
    gallery_qs = ListingImage.objects.filter(listing=item) if item else ListingImage.objects.none()
    formset = ListingImageFormSet(
        request.POST or None, request.FILES or None, queryset=gallery_qs, prefix="gallery"
    )
    photo_err = None
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        photo_err = photo_count_error(form, formset)
        if photo_err:
            messages.error(request, photo_err)
    if request.method == "POST" and photo_err is None and form.is_valid() and formset.is_valid():
        saved = form.save(owner=request.user)
        from .videos import start_video_job
        for img in formset.save(commit=False):
            img.listing = saved
            img.save()
        for obj in formset.deleted_objects:
            obj.delete()
        from .models import SiteSettings
        _ss = SiteSettings.objects.first()
        if not item and _ss and _ss.moderate_new_listings:
            saved.is_active = False
            saved.pending_review = True
            saved.save(update_fields=["is_active", "pending_review"])
            emails.notify_staff_pending_listing(saved)
            messages.success(request, "İlanın incelemeye alındı, onaylanınca yayınlanacak.")
        else:
            messages.success(request, "İlan yayınlandı." if not item else "İlan güncellendi.")
        start_video_job(saved)
        return redirect("market:my_listings")
    return render(request, "market/mylistings/form.html",
                  {"form": form, "formset": formset, "item": item})


@login_required
def my_listing_delete(request, pk):
    item = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == "POST":
        item.delete()
        messages.success(request, "İlan silindi.")
        return redirect("market:my_listings")
    return render(request, "market/mylistings/delete.html", {"item": item})


# ---------------------------------------------------------------------------
# Sepet / odeme (yalniz magaza urunleri)
# ---------------------------------------------------------------------------
def _cart_dict(request):
    return request.session.setdefault(CART_KEY, {})


def _cart_key(listing_id, variant_id=None):
    return f"{listing_id}:{variant_id}" if variant_id else str(listing_id)


def _cart_lines(request):
    """Sepet satirlarini cozer. Varyantli urunlerde stok kontrolu ve fiyat farki dahil edilir."""
    cart = _cart_dict(request)
    lines, total, out_of_stock = [], Decimal("0"), []
    for key, qty in list(cart.items()):
        qty = int(qty)
        listing_id, _, variant_id = str(key).partition(":")
        item = Listing.objects.filter(pk=listing_id, mode=Mode.SHOP, is_active=True).select_related(
            "shop", "country"
        ).first()
        if not item:
            continue
        variant = ListingVariant.objects.filter(pk=variant_id).first() if variant_id else None
        available = variant.stock if variant else (item.stock if item.track_stock else None)
        if available is not None and available <= 0:
            out_of_stock.append(item)
            continue
        if available is not None:
            qty = min(qty, available)
        unit_price = variant.final_price_eur if variant else item.price_eur
        line_total = unit_price * qty
        total += line_total
        lines.append({"item": item, "variant": variant, "qty": qty,
                      "unit_price": unit_price, "line_total": line_total, "key": key})
    return lines, total, out_of_stock


def cart_view(request):
    lines, total, out_of_stock = _cart_lines(request)
    country = _current_country(request)
    return render(request, "market/cart/cart.html",
                  {"lines": lines, "total": total, "country": country, "out_of_stock": out_of_stock})


def cart_add(request, pk):
    item = get_object_or_404(Listing, pk=pk, mode=Mode.SHOP, is_active=True)
    variant_id = request.POST.get("variant") or request.GET.get("variant") or ""
    variant = None
    if item.variants.exists():
        variant = item.variants.filter(pk=variant_id).first()
        if not variant:
            messages.error(request, "Lütfen önce bir seçenek (beden/renk) seç.")
            return redirect("market:listing_detail", pk=item.pk, slug=item.slug)
        if variant.stock <= 0:
            messages.error(request, "Bu seçenek stokta yok.")
            return redirect("market:listing_detail", pk=item.pk, slug=item.slug)
    elif item.track_stock and (item.stock or 0) <= 0:
        messages.error(request, "Bu ürün şu anda stokta yok.")
        return redirect("market:listing_detail", pk=item.pk, slug=item.slug)

    cart = _cart_dict(request)
    key = _cart_key(pk, variant.pk if variant else None)
    cart[key] = int(cart.get(key, 0)) + 1
    request.session.modified = True
    messages.success(request, f"{item.title} sepete eklendi.")
    return redirect(request.META.get("HTTP_REFERER") or "market:cart")


def cart_set_qty(request, key):
    if request.method == "POST":
        cart = _cart_dict(request)
        qty = max(1, min(20, int(request.POST.get("qty", 1) or 1)))
        if key in cart:
            cart[key] = qty
            request.session.modified = True
    return redirect("market:cart")


def cart_remove(request, key):
    cart = _cart_dict(request)
    cart.pop(key, None)
    request.session.modified = True
    return redirect("market:cart")


def _stripe_ready():
    return bool(settings.STRIPE_SECRET_KEY)


def _apply_coupon(code, shop_ids, subtotal):
    """Kupon dogrular; (coupon, discount) ya da (None, 0) dondurur."""
    if not code:
        return None, Decimal("0")
    coupon = Coupon.objects.filter(code__iexact=code.strip()).first()
    if not coupon or not coupon.is_valid:
        return None, Decimal("0")
    if coupon.shop_id and coupon.shop_id not in shop_ids:
        return None, Decimal("0")
    return coupon, coupon.discount_for(subtotal)


def _restock(order):
    """Siparis iptal edilince stogu geri ekler."""
    for it in order.items.all():
        if it.variant:
            it.variant.stock += it.qty
            it.variant.save(update_fields=["stock"])
        elif it.listing and it.listing.track_stock:
            it.listing.stock = (it.listing.stock or 0) + it.qty
            it.listing.save(update_fields=["stock"])


def _decrement_stock(order):
    for it in order.items.all():
        if it.variant:
            it.variant.stock = max(0, it.variant.stock - it.qty)
            it.variant.save(update_fields=["stock"])
        elif it.listing and it.listing.track_stock:
            it.listing.stock = max(0, (it.listing.stock or 0) - it.qty)
            it.listing.save(update_fields=["stock"])


def _mark_order_paid(order):
    """Tum 'odendi' yollarinin (demo/stripe basari/webhook) ortak son adimi."""
    if order.status == OrderStatus.PAID:
        return
    order.status = OrderStatus.PAID
    order.paid_at = timezone.now()
    order.save(update_fields=["status", "paid_at"])
    _decrement_stock(order)
    if order.coupon_id:
        Coupon.objects.filter(pk=order.coupon_id).update(used_count=models.F("used_count") + 1)
    emails.notify_order_paid_buyer(order)
    emails.notify_order_paid_sellers(order)


@login_required
def checkout(request):
    lines, total, out_of_stock = _cart_lines(request)
    country = _current_country(request)
    if not lines:
        return redirect("market:cart")

    coupon_code = request.POST.get("coupon_code", "") if request.method == "POST" else request.GET.get("coupon_code", "")
    shop_ids = {line["item"].shop_id for line in lines if line["item"].shop_id}
    coupon, discount = _apply_coupon(coupon_code, shop_ids, total)
    final_total = max(Decimal("0"), total - discount)

    if request.method == "POST":
        # Sepetteki stoklari son kez dogrula (yarista baskasi tuketmis olabilir).
        for line in lines:
            available = line["variant"].stock if line["variant"] else (
                line["item"].stock if line["item"].track_stock else None
            )
            if available is not None and available < line["qty"]:
                messages.error(request, f"{line['item'].title}: yeterli stok kalmadı.")
                return redirect("market:cart")

        order = Order.objects.create(
            buyer=request.user, country=country, status=OrderStatus.PENDING, total_eur=final_total,
            full_name=request.POST.get("full_name", "").strip() or request.user.get_full_name(),
            address=request.POST.get("address", "").strip(),
            phone=request.POST.get("phone", "").strip(),
            coupon=coupon, discount_eur=discount,
        )
        for line in lines:
            OrderItem.objects.create(
                order=order, listing=line["item"], variant=line["variant"], shop=line["item"].shop,
                title=line["item"].title, variant_name=line["variant"].name if line["variant"] else "",
                price_eur=line["unit_price"], qty=line["qty"],
            )

        if _stripe_ready():
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            success_url = (settings.SITE_URL + reverse("market:order_payment_success")
                            + "?session_id={CHECKOUT_SESSION_ID}&order=" + str(order.pk))
            cancel_url = settings.SITE_URL + reverse("market:cart")
            if discount > 0:
                stripe_line_items = [{
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": f"Sepet (kupon: {coupon.code})"},
                        "unit_amount": int(final_total * 100),
                    },
                    "quantity": 1,
                }]
            else:
                stripe_line_items = [{
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": item_line["item"].title
                                          + (f" — {item_line['variant'].name}" if item_line["variant"] else "")},
                        "unit_amount": int(item_line["unit_price"] * 100),
                    },
                    "quantity": item_line["qty"],
                } for item_line in lines]
            try:
                session = stripe.checkout.Session.create(
                    mode="payment", payment_method_types=["card"],
                    customer_email=request.user.email or None,
                    line_items=stripe_line_items,
                    success_url=success_url, cancel_url=cancel_url,
                    metadata={"order_id": str(order.pk)},
                )
            except Exception:
                log.exception("Stripe checkout session olusturulamadi")
                messages.error(request, "Ödeme başlatılamadı, lütfen tekrar dene.")
                order.delete()
                return redirect("market:cart")
            order.stripe_session_id = session.id
            order.save(update_fields=["stripe_session_id"])
            return redirect(session.url, permanent=False)

        # Stripe anahtari tanimli degil -> demo akis: siparis dogrudan odenmis sayilir.
        order.payment_method = "cod"
        order.save(update_fields=["payment_method"])
        _mark_order_paid(order)
        request.session[CART_KEY] = {}
        request.session.modified = True
        return redirect("market:order_success", pk=order.pk)

    return render(request, "market/cart/checkout.html",
                  {"lines": lines, "total": total, "discount": discount, "final_total": final_total,
                   "coupon": coupon, "coupon_code": coupon_code, "country": country,
                   "stripe_ready": _stripe_ready()})


@login_required
def order_payment_success(request):
    """Stripe hosted checkout'tan basari donusu. Odemeyi dogrulayip siparisi isaretler."""
    order_id = request.GET.get("order")
    session_id = request.GET.get("session_id")
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    if order.status != OrderStatus.PAID and session_id and _stripe_ready():
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid" and str(session.metadata.get("order_id")) == str(order.pk):
                _mark_order_paid(order)
        except Exception:
            log.exception("Stripe session dogrulanamadi")
    if order.status == OrderStatus.PAID:
        request.session[CART_KEY] = {}
        request.session.modified = True
    return redirect("market:order_success", pk=order.pk)


@csrf_exempt
def stripe_webhook(request):
    """Stripe'in sunucudan sunucuya bildirim endpoint'i (guvenlik agi).

    Basari sayfasi zaten siparisi isaretler; bu endpoint sekme kapatilsa da
    odemenin isaretlenmesini garanti eder. STRIPE_WEBHOOK_SECRET bossa devre disi.
    """
    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponse(status=204)
    import stripe
    payload = request.body
    sig = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        log.exception("Stripe webhook dogrulama hatasi")
        return HttpResponseBadRequest()

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        meta = session.get("metadata") or {}
        order_id = meta.get("order_id")
        boost_id = meta.get("boost_id")
        if order_id:
            order = Order.objects.filter(pk=order_id, status=OrderStatus.PENDING).first()
            if order:
                _mark_order_paid(order)
        elif boost_id:
            boost = Boost.objects.filter(pk=boost_id, status=BoostStatus.PENDING).first()
            if boost:
                boost.apply()
    return HttpResponse(status=200)


@login_required
def order_cancel(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    if request.method == "POST" and order.can_cancel:
        _restock(order)
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = timezone.now()
        order.save(update_fields=["status", "cancelled_at"])
        emails.notify_order_cancelled(order)
        messages.success(request, "Siparişin iptal edildi.")
    return redirect("market:my_orders")


def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    return render(request, "market/cart/order_success.html", {"order": order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(buyer=request.user).prefetch_related("items")
    return render(request, "market/cart/orders.html", {"orders": orders})


# ---------------------------------------------------------------------------
# Mesajlasma
# ---------------------------------------------------------------------------
def _listing_owner(listing):
    if listing.mode == Mode.SHOP and listing.shop and listing.shop.owner:
        return listing.shop.owner
    return listing.owner


def _is_blocked(a, b):
    from .models import UserBlock
    return UserBlock.objects.filter(Q(blocker=a, blocked=b) | Q(blocker=b, blocked=a)).exists()


@login_required
def block_user(request, pk):
    from .models import UserBlock
    target = get_object_or_404(User, pk=pk)
    if request.method == "POST" and target != request.user:
        UserBlock.objects.get_or_create(blocker=request.user, blocked=target)
        messages.success(request, "Kullanici engellendi.")
    return redirect("market:inbox")


@login_required
def start_conversation(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    other = _listing_owner(listing)
    if not other or other == request.user:
        messages.error(request, "Bu ilan için mesajlaşma şu anda kullanılamıyor.")
        return redirect("market:listing_detail", pk=listing.pk, slug=listing.slug)
    if _is_blocked(request.user, other):
        messages.error(request, "Bu kullanici ile mesajlasamazsin.")
        return redirect("market:listing_detail", pk=listing.pk, slug=listing.slug)
    a, b = sorted([request.user, other], key=lambda u: u.pk)
    conversation, _ = Conversation.objects.get_or_create(
        listing=listing, participant_a=a, participant_b=b
    )
    return redirect("market:message_thread", pk=conversation.pk)


@login_required
def inbox(request):
    convos = (Conversation.objects.filter(Q(participant_a=request.user) | Q(participant_b=request.user))
              .select_related("listing", "participant_a", "participant_b")
              .prefetch_related("messages"))
    rows = []
    for c in convos:
        last = c.last_message()
        rows.append({"c": c, "other": c.other(request.user), "last": last,
                     "unread": c.messages.filter(is_read=False).exclude(sender=request.user).count()})
    rows.sort(key=lambda r: r["last"].created_at if r["last"] else r["c"].created_at, reverse=True)
    return render(request, "market/messages/inbox.html", {"rows": rows})


@login_required
def message_thread(request, pk):
    conversation = get_object_or_404(
        Conversation.objects.select_related("listing", "participant_a", "participant_b"), pk=pk
    )
    if request.user not in (conversation.participant_a, conversation.participant_b):
        messages.error(request, "Bu sohbete erişimin yok.")
        return redirect("market:inbox")
    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        from datetime import timedelta
        if body and _is_blocked(request.user, conversation.other(request.user)):
            messages.error(request, "Bu kullanici ile mesajlasamazsin.")
            return redirect("market:inbox")
        if body and Message.objects.filter(sender=request.user, created_at__gte=timezone.now() - timedelta(seconds=60)).count() >= 8:
            messages.error(request, "Cok hizli mesaj gonderiyorsun, biraz bekle.")
            return redirect("market:message_thread", pk=pk)
        if body:
            msg = Message.objects.create(conversation=conversation, sender=request.user, body=body)
            Conversation.objects.filter(pk=conversation.pk).update(updated_at=timezone.now())
            from . import push
            push.notify_new_message(msg)
            # E-posta birlestirme: ayni kisiden okunmamis ve zaten bildirilmis mesaj varsa (30 dk) tekrar e-posta gonderme
            already = (Message.objects.filter(conversation=conversation, sender=request.user, is_read=False,
                                              notified=True, created_at__gte=timezone.now() - timedelta(minutes=30))
                       .exclude(pk=msg.pk).exists())
            if not already:
                emails.notify_new_message(msg)
                Message.objects.filter(pk=msg.pk).update(notified=True)
        return redirect("market:message_thread", pk=pk)
    conversation.messages.exclude(sender=request.user).update(is_read=True)
    return render(request, "market/messages/thread.html",
                  {"conversation": conversation, "other": conversation.other(request.user),
                   "thread_messages": conversation.messages.select_related("sender")})


# ---------------------------------------------------------------------------
# Ilan one cikarma (ucretli vitrin)
# ---------------------------------------------------------------------------
def _can_boost(user, listing):
    return listing.owner == user or (listing.shop and listing.shop.owner == user)


@login_required
def boost_options(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if not _can_boost(request.user, listing):
        messages.error(request, "Bu ilanı öne çıkaramazsın.")
        return redirect("market:listing_detail", pk=listing.pk, slug=listing.slug)
    return render(request, "market/boost/options.html",
                  {"listing": listing, "packages": settings.BOOST_PACKAGES})


@login_required
def boost_checkout(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if not _can_boost(request.user, listing):
        messages.error(request, "Bu ilanı öne çıkaramazsın.")
        return redirect("market:listing_detail", pk=listing.pk, slug=listing.slug)
    try:
        days = int(request.POST.get("days", 0))
    except ValueError:
        days = 0
    package = next((p for p in settings.BOOST_PACKAGES if p["days"] == days), None)
    if not package:
        messages.error(request, "Geçersiz paket.")
        return redirect("market:boost_options", listing_id=listing.pk)

    boost = Boost.objects.create(
        listing=listing, buyer=request.user, days=package["days"], price_eur=package["price_eur"]
    )

    if _stripe_ready():
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        success_url = (settings.SITE_URL + reverse("market:boost_payment_success")
                        + "?session_id={CHECKOUT_SESSION_ID}&boost=" + str(boost.pk))
        cancel_url = settings.SITE_URL + reverse(
            "market:listing_detail", args=[listing.pk, listing.slug]
        )
        try:
            session = stripe.checkout.Session.create(
                mode="payment", payment_method_types=["card"],
                customer_email=request.user.email or None,
                line_items=[{
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": f"Vitrin — {listing.title} ({boost.days} gün)"},
                        "unit_amount": int(boost.price_eur * 100),
                    },
                    "quantity": 1,
                }],
                success_url=success_url, cancel_url=cancel_url,
                metadata={"boost_id": str(boost.pk)},
            )
        except Exception:
            log.exception("Stripe boost session olusturulamadi")
            messages.error(request, "Ödeme başlatılamadı, lütfen tekrar dene.")
            boost.delete()
            return redirect("market:listing_detail", pk=listing.pk, slug=listing.slug)
        boost.stripe_session_id = session.id
        boost.save(update_fields=["stripe_session_id"])
        return redirect(session.url, permanent=False)

    # Demo akis: Stripe tanimli degilse dogrudan uygula.
    boost.apply()
    messages.success(request, f"{listing.title} {boost.days} gün süreyle öne çıkarıldı.")
    return redirect("market:listing_detail", pk=listing.pk, slug=listing.slug)


@login_required
def boost_payment_success(request):
    boost_id = request.GET.get("boost")
    session_id = request.GET.get("session_id")
    boost = get_object_or_404(Boost, pk=boost_id, buyer=request.user)
    if boost.status != BoostStatus.PAID and session_id and _stripe_ready():
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid" and str(session.metadata.get("boost_id")) == str(boost.pk):
                boost.apply()
        except Exception:
            log.exception("Stripe boost session dogrulanamadi")
    if boost.status == BoostStatus.PAID:
        messages.success(request, f"{boost.listing.title} {boost.days} gün süreyle öne çıkarıldı.")
    return redirect("market:listing_detail", pk=boost.listing.pk, slug=boost.listing.slug)


# ---------------------------------------------------------------------------
# Favoriler
# ---------------------------------------------------------------------------
@login_required
def favorite_toggle_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, listing=listing)
    if not created:
        fav.delete()
    if request.headers.get("x-requested-with") == "fetch":
        return JsonResponse({"on": created})
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    return redirect(next_url or "market:home")


@login_required
def favorite_toggle_shop(request, pk):
    shop = get_object_or_404(Shop, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, shop=shop)
    if not created:
        fav.delete()
    return redirect(request.META.get("HTTP_REFERER") or "market:shop_detail", slug=shop.slug)


@login_required
def my_favorites(request):
    listings = Listing.objects.filter(favorited_by__user=request.user).select_related("city", "shop")
    shops = Shop.objects.filter(favorited_by__user=request.user).select_related("city", "country")
    return render(request, "market/favorites.html", {"listings": listings, "shops": shops})


# ---------------------------------------------------------------------------
# Degerlendirme / yorum
# ---------------------------------------------------------------------------
@login_required
def review_create(request, order_item_id):
    item = get_object_or_404(
        OrderItem, pk=order_item_id, order__buyer=request.user, order__status=OrderStatus.PAID
    )
    if hasattr(item, "review"):
        return redirect("market:my_orders")
    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        Review.objects.create(
            order_item=item, listing=item.listing, author=request.user,
            rating=int(form.cleaned_data["rating"]), comment=form.cleaned_data["comment"],
        )
        messages.success(request, "Yorumun için teşekkürler.")
        return redirect("market:my_orders")
    return render(request, "market/review_form.html", {"form": form, "item": item})


@login_required
def report_listing(request, pk):
    from .models import ListingReport
    item = get_object_or_404(Listing, pk=pk)
    if request.method == "POST":
        text = request.POST.get("message", "").strip()[:1000]
        if text:
            rep = ListingReport.objects.create(listing=item, reporter=request.user, message=text)
            emails.notify_staff_report(rep)
            messages.success(request, "Sikayetin alindi, tesekkurler.")
        else:
            messages.error(request, "Lutfen sikayet metnini yaz.")
    return redirect("market:listing_detail", pk=item.pk, slug=item.slug)


@login_required
def renew_listing(request, pk):
    item = get_object_or_404(Listing, pk=pk, owner=request.user)
    if request.method == "POST":
        item.is_active = True
        item.pending_review = False
        item.created_at = timezone.now()
        item.save(update_fields=["is_active", "pending_review", "created_at"])
        messages.success(request, "Ilan yenilendi.")
    return redirect("market:my_listings")


def seller_profile(request, pk):
    from django.core.paginator import Paginator
    seller = get_object_or_404(User, pk=pk, is_active=True)
    qs = Listing.objects.filter(owner=seller, is_active=True, shop__isnull=True).select_related("city")
    page = Paginator(qs, 24).get_page(request.GET.get("page"))
    from .models import SellerReview, can_review_seller, seller_rating
    avg, n = seller_rating(seller)
    return render(request, "market/seller.html", {
        "seller": seller, "page_obj": page, "rating_avg": avg, "rating_n": n,
        "reviews": SellerReview.objects.filter(seller=seller).select_related("author")[:20],
        "can_review": can_review_seller(request.user, seller)})


@login_required
def push_subscribe(request):
    """Tarayicinin gonderdigi anlik bildirim aboneligini kaydeder."""
    import json
    from .models import PushSubscription
    if request.method != "POST":
        return HttpResponseBadRequest("POST")
    try:
        data = json.loads(request.body.decode("utf-8"))
        endpoint = data["endpoint"]
        keys = data["keys"]
        PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={"user": request.user, "p256dh": keys["p256dh"], "auth": keys["auth"]},
        )
    except Exception:
        return HttpResponseBadRequest("bad subscription")
    return HttpResponse("ok")


@login_required
def messages_status(request):
    """Okunmamis mesaj sayisi (sayfa her birkac saniyede bir sorar, rozetler aninda guncellenir)."""
    u = request.user
    n = (Message.objects.filter(is_read=False)
         .filter(Q(conversation__participant_a=u) | Q(conversation__participant_b=u))
         .exclude(sender=u).count())
    resp = JsonResponse({"unread": n})
    resp["Cache-Control"] = "no-store"
    return resp


@login_required
def save_search(request):
    from django.http import QueryDict
    from .models import SavedSearch
    if request.method != "POST":
        return redirect("market:listings")
    qs = request.POST.get("qs", "")[:500]
    label = request.POST.get("label", "").strip()[:120] or "Arama"
    country = _current_country(request)
    if SavedSearch.objects.filter(user=request.user).count() >= 10 and not SavedSearch.objects.filter(user=request.user, params=qs).exists():
        messages.error(request, "En fazla 10 arama kaydedebilirsin.")
    else:
        mode = QueryDict(qs).get("mode") or Mode.USED
        SavedSearch.objects.get_or_create(user=request.user, params=qs,
                                          defaults={"label": label, "country": country, "mode": mode})
        messages.success(request, "Arama kaydedildi. Yeni ilan gelince haber vereceğiz.")
    return redirect(reverse("market:listings") + ("?" + qs if qs else ""))


@login_required
def saved_searches(request):
    from .models import SavedSearch
    return render(request, "market/saved_searches.html",
                  {"searches": SavedSearch.objects.filter(user=request.user)})


@login_required
def delete_saved_search(request, pk):
    from .models import SavedSearch
    if request.method == "POST":
        SavedSearch.objects.filter(pk=pk, user=request.user).delete()
    return redirect("market:saved_searches")


@login_required
def review_seller(request, pk):
    from .models import SellerReview, can_review_seller
    seller = get_object_or_404(User, pk=pk, is_active=True)
    if request.method == "POST" and can_review_seller(request.user, seller):
        try:
            rating = int(request.POST.get("rating", 0))
        except ValueError:
            rating = 0
        if 1 <= rating <= 5:
            SellerReview.objects.create(seller=seller, author=request.user, rating=rating,
                                        comment=request.POST.get("comment", "").strip()[:500])
            messages.success(request, "Degerlendirmen kaydedildi, tesekkurler.")
    return redirect("market:seller_profile", pk=seller.pk)


@login_required
def verification_doc(request, pk):
    """Dogrulama belgesini yalnizca yoneticiler acabilir."""
    from django.http import FileResponse, Http404
    from .models import VerificationRequest
    if not request.user.is_staff:
        raise Http404
    vr = get_object_or_404(VerificationRequest, pk=pk)
    return FileResponse(vr.document.open("rb"))
