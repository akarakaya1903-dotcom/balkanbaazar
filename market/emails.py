# -*- coding: utf-8 -*-
"""Bildirim e-postalari.

Basit ve merkezi tutuldu: her fonksiyon konu + govde hazirlar, ortak _send()
ile gonderir. Govdeler TR + EN iki dilli (kisa) tutuldu, cunku kullanicinin
tercih dili suanda oturumda tutuluyor, kullanicida kalici bir dil alani yok.
Gonderim basarisiz olursa istek akisini bozmamasi icin hata loglanir, exception
yukariya firlatilmaz (fail_silently mantigi elle uygulanir).
"""
import logging

from django.conf import settings
from django.core.mail import send_mail

log = logging.getLogger(__name__)


def _send(subject, body, to):
    to = [addr for addr in (to if isinstance(to, (list, tuple)) else [to]) if addr]
    if not to:
        return
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, to, fail_silently=False)
    except Exception:
        log.exception("E-posta gonderilemedi: %s -> %s", subject, to)


def _site(path):
    return settings.SITE_URL.rstrip("/") + path


# ---------------------------------------------------------------------------
# Magaza basvurusu
# ---------------------------------------------------------------------------
def notify_application_received(application):
    subject = f"[Balkan Baazar] Başvurun alındı — {application.shop_name}"
    body = (
        f"Merhaba {application.contact_name},\n\n"
        f"\"{application.shop_name}\" için mağaza başvurun alındı. Ekibimiz iki iş günü "
        f"içinde dönecek. Durumu buradan takip edebilirsin:\n{_site('/panel/')}\n\n"
        "— Balkan Baazar\n\n"
        "---\n\n"
        f"Hi {application.contact_name},\n\n"
        f"Your shop application for \"{application.shop_name}\" was received. We'll get "
        f"back to you within two business days. Track its status here:\n{_site('/panel/')}\n\n"
        "— Balkan Baazar"
    )
    _send(subject, body, application.email)


def notify_staff_new_application(application):
    if not settings.STAFF_NOTIFY_EMAILS:
        return
    subject = f"[Yönetim] Yeni mağaza başvurusu — {application.shop_name}"
    body = (
        f"{application.shop_name} ({application.country.name_tr}) yeni bir mağaza başvurusu yaptı.\n"
        f"Başvuran: {application.contact_name} <{application.email}>\n\n"
        f"Onaylamak veya reddetmek için:\n{_site('/yonetim/basvurular/')}"
    )
    _send(subject, body, settings.STAFF_NOTIFY_EMAILS)


def notify_application_approved(application, shop):
    subject = f"[Balkan Baazar] Mağazan onaylandı — {shop.name}"
    body = (
        f"Merhaba {application.contact_name},\n\n"
        f"\"{shop.name}\" onaylandı ve açıldı — ilk üç ay ücretsiz. Panelinden ürün "
        f"yüklemeye hemen başlayabilirsin:\n{_site('/panel/')}\n\n"
        "— Balkan Baazar\n\n"
        "---\n\n"
        f"Hi {application.contact_name},\n\n"
        f"\"{shop.name}\" has been approved and is now open — first three months free. "
        f"You can start uploading products right away:\n{_site('/panel/')}\n\n"
        "— Balkan Baazar"
    )
    _send(subject, body, application.email)


def notify_application_rejected(application):
    subject = f"[Balkan Baazar] Başvurun hakkında — {application.shop_name}"
    note = f"\nNot: {application.staff_note}\n" if application.staff_note else ""
    body = (
        f"Merhaba {application.contact_name},\n\n"
        f"\"{application.shop_name}\" başvurun bu kez onaylanmadı.{note}\n"
        "Sorularin için bize yazabilirsin.\n\n"
        "— Balkan Baazar\n\n"
        "---\n\n"
        f"Hi {application.contact_name},\n\n"
        f"Your application for \"{application.shop_name}\" was not approved this time.{note}\n"
        "Feel free to reach out with any questions.\n\n"
        "— Balkan Baazar"
    )
    _send(subject, body, application.email)


# ---------------------------------------------------------------------------
# Mesajlasma
# ---------------------------------------------------------------------------
def notify_new_message(message):
    conversation = message.conversation
    recipient = conversation.other(message.sender)
    if not recipient.email:
        return
    sender_name = message.sender.get_full_name() or message.sender.username
    subject = f"[Balkan Baazar] {sender_name} sana mesaj gönderdi"
    listing_line = f"İlan: {conversation.listing.title}\n" if conversation.listing else ""
    body = (
        f"{sender_name}: \"{message.body[:200]}\"\n\n"
        f"{listing_line}"
        f"Yanıtlamak için:\n{_site('/mesaj/' + str(conversation.pk) + '/')}\n\n"
        "— Balkan Baazar\n\n"
        "---\n\n"
        f"{sender_name} sent you a message: \"{message.body[:200]}\"\n\n"
        f"Reply here:\n{_site('/mesaj/' + str(conversation.pk) + '/')}\n\n"
        "— Balkan Baazar"
    )
    _send(subject, body, recipient.email)


# ---------------------------------------------------------------------------
# Siparis
# ---------------------------------------------------------------------------
def notify_order_paid_buyer(order):
    subject = f"[Balkan Baazar] Siparişin alındı — #{order.pk}"
    lines = "\n".join(f"- {it.title} × {it.qty} — € {it.line_total_eur:.0f}" for it in order.items.all())
    body = (
        f"Merhaba {order.full_name or order.buyer.username},\n\n"
        f"#{order.pk} numaralı siparişin ödendi. İçerik:\n{lines}\n\nToplam: € {order.total_eur:.0f}\n\n"
        f"Siparişlerin:\n{_site('/siparislerim/')}\n\n— Balkan Baazar\n\n"
        "---\n\n"
        f"Hi {order.full_name or order.buyer.username},\n\n"
        f"Order #{order.pk} has been paid. Items:\n{lines}\n\nTotal: € {order.total_eur:.0f}\n\n"
        f"Your orders:\n{_site('/siparislerim/')}\n\n— Balkan Baazar"
    )
    _send(subject, body, order.buyer.email)


def notify_order_paid_sellers(order):
    by_shop = {}
    for item in order.items.all():
        if item.shop:
            by_shop.setdefault(item.shop, []).append(item)
    for shop, items in by_shop.items():
        if not shop.owner or not shop.owner.email:
            continue
        lines = "\n".join(f"- {it.title} × {it.qty} — € {it.line_total_eur:.0f}" for it in items)
        subject = f"[Balkan Baazar] Yeni sipariş — {shop.name}"
        body = (
            f"{shop.name} için yeni bir sipariş var (#{order.pk}):\n{lines}\n\n"
            f"Panelden görüntüle:\n{_site('/panel/')}\n\n— Balkan Baazar\n\n"
            "---\n\n"
            f"{shop.name} has a new order (#{order.pk}):\n{lines}\n\n"
            f"View in your panel:\n{_site('/panel/')}\n\n— Balkan Baazar"
        )
        _send(subject, body, shop.owner.email)


def notify_order_shipped(order_item):
    order = order_item.order
    if not order.buyer.email:
        return
    subject = f"[Balkan Baazar] Kargoya verildi — {order_item.title}"
    body = (
        f"Merhaba {order.full_name or order.buyer.username},\n\n"
        f"\"{order_item.title}\" kargoya verildi.\n"
        f"Kargo: {order_item.carrier or '-'}  Takip no: {order_item.tracking_number or '-'}\n\n"
        f"Siparişlerin:\n{_site('/siparislerim/')}\n\n— Balkan Baazar\n\n"
        "---\n\n"
        f"Hi {order.full_name or order.buyer.username},\n\n"
        f"\"{order_item.title}\" has been shipped.\n"
        f"Carrier: {order_item.carrier or '-'}  Tracking: {order_item.tracking_number or '-'}\n\n"
        f"Your orders:\n{_site('/siparislerim/')}\n\n— Balkan Baazar"
    )
    _send(subject, body, order.buyer.email)


def notify_order_cancelled(order):
    subject = f"[Balkan Baazar] Sipariş iptal edildi — #{order.pk}"
    body = (
        f"#{order.pk} numaralı siparişin iptal edildi.\n\n— Balkan Baazar\n\n"
        "---\n\n"
        f"Order #{order.pk} has been cancelled.\n\n— Balkan Baazar"
    )
    _send(subject, body, order.buyer.email)
    by_shop = {}
    for item in order.items.all():
        if item.shop and item.shop.owner and item.shop.owner.email:
            by_shop.setdefault(item.shop, True)
    for shop in by_shop:
        _send(f"[Balkan Baazar] Sipariş iptal edildi — #{order.pk}",
              f"{shop.name} için #{order.pk} numaralı sipariş iptal edildi.\n\n— Balkan Baazar",
              shop.owner.email)


def notify_staff_new_user(user):
    """Yeni uye kaydini yoneticilere (STAFF_NOTIFY_EMAILS) bildirir."""
    body = (f"Yeni uye kaydi\n\nKullanici adi: {user.username}\nAd: {user.first_name} {user.last_name}\n"
            f"E-posta: {user.email}\n\nYonetim: {_site('/admin/auth/user/')}")
    _send(f"Yeni uye: {user.username}", body, settings.STAFF_NOTIFY_EMAILS)


def welcome_user(user):
    if not user.email:
        return
    name = user.first_name or user.username
    _send("Balkan Baazar - Hos geldin / Welcome",
          f"Merhaba {name},\n\nBalkan Baazar'a hos geldin. Hesabin hazir: {_site('/')}\n\n"
          f"Hi {name},\n\nWelcome to Balkan Baazar. Your account is ready: {_site('/')}\n",
          user.email)


def notify_password_changed(user):
    if not user.email:
        return
    name = user.first_name or user.username
    _send("Balkan Baazar - Sifren degistirildi / Password changed",
          f"Merhaba {name},\n\nHesabinin sifresi az once degistirildi. Bunu sen yapmadiysan hemen "
          f"{_site('/uyelik/sifre-sifirla/')} adresinden sifreni yenile ve bizimle iletisime gec.\n\n"
          f"Hi {name},\n\nYour account password was just changed. If this wasn't you, reset it right away at "
          f"{_site('/uyelik/sifre-sifirla/')} and contact us.\n",
          user.email)


def notify_staff_report(report):
    body = (f"Yeni ilan sikayeti\n\nIlan: {report.listing.title} ({_site('/ilan/%d/%s/' % (report.listing_id, report.listing.slug))})\n"
            f"Sikayet eden: {report.reporter or 'anonim'}\n\n{report.message}\n\nYonetim: {_site('/admin/market/listingreport/')}")
    _send(f"Ilan sikayeti #{report.pk}", body, settings.STAFF_NOTIFY_EMAILS)


def notify_staff_pending_listing(listing):
    _send(f"Onay bekleyen ilan: {listing.title}",
          f"Yeni bir ilan onay bekliyor.\n\nBaslik: {listing.title}\nFiyat: {listing.price_eur}\n\nOnaylamak icin: {_site('/admin/market/listing/?pending_review__exact=1')}",
          settings.STAFF_NOTIFY_EMAILS)


def verification_link(user):
    from django.core import signing
    token = signing.dumps({"u": user.pk, "e": user.email}, salt="bb-verify")
    return _site(f"/uyelik/dogrula/{token}/")


def send_verification(user):
    if not user.email:
        return
    link = verification_link(user)
    _send("Balkan Baazar - E-postani dogrula / Verify your email",
          f"Merhaba,\n\nE-posta adresini dogrulamak icin su baglantiya tikla (3 gun gecerli):\n{link}\n\n"
          f"Hi,\n\nPlease verify your email address with this link (valid for 3 days):\n{link}\n",
          user.email)


def notify_saved_search(search, listings, count):
    """Kayitli aramaya uyan yeni ilanlari tek e-postada ozetler."""
    user = search.user
    if not user.email:
        return
    lines = "\n".join(f"- {l.title} ({l.price_eur} EUR)\n  {_site('/ilan/%d/%s/' % (l.pk, l.slug))}" for l in listings)
    more = f"\n... ve {count - len(listings)} ilan daha." if count > len(listings) else ""
    link = _site("/ilanlar/?" + search.params)
    _send(f"[Balkan Baazar] Yeni ilanlar: {search.label}",
          f"Kayıtlı aramana uyan {count} yeni ilan var: {search.label}\n\n{lines}{more}\n\nTümünü gör: {link}\n"
          f"Aramalarını yönet: {_site('/kayitli-aramalar/')}\n\n---\n\n"
          f"{count} new listing(s) match your saved search: {search.label}\nSee all: {link}\n",
          user.email)


def notify_staff_verification(vr):
    _send(f"Dogrulama basvurusu: {vr.shop.name}",
          f"{vr.shop.name} magazasi dogrulama icin belge yukledi.\n\nInceleme: {_site('/admin/market/verificationrequest/')}",
          settings.STAFF_NOTIFY_EMAILS)


def notify_verification_result(vr):
    owner = vr.shop.owner
    if not owner or not owner.email:
        return
    if vr.status == "approved":
        tr = f"Harika! {vr.shop.name} mağazan doğrulandı. Mağaza sayfanda ve ilanlarında ✔ rozeti görünecek."
        en = f"Great news! Your shop {vr.shop.name} has been verified. The ✔ badge now shows on your shop and listings."
    else:
        why = f" Not: {vr.admin_note}" if vr.admin_note else ""
        tr = f"{vr.shop.name} mağazanın doğrulama başvurusu onaylanamadı.{why} Belgeni yeniden yükleyebilirsin."
        en = f"Your verification request for {vr.shop.name} could not be approved.{(' Note: ' + vr.admin_note) if vr.admin_note else ''} You can upload a new document."
    _send("Balkan Baazar - Mağaza doğrulama / Shop verification", f"{tr}\n\n---\n\n{en}\n", owner.email)
