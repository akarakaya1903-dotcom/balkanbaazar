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


def lang_of(request):
    """Istek sahibinin sitede sectigi dil (yoksa varsayilan)."""
    try:
        return getattr(request, "lang_override", None) or request.session.get("lang") or settings.DEFAULT_LANG
    except Exception:
        return settings.DEFAULT_LANG


def _send(subject, body, to, html=None):
    to = [addr for addr in (to if isinstance(to, (list, tuple)) else [to]) if addr]
    if not to:
        return
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, to, fail_silently=False, html_message=html)
    except Exception:
        log.exception("E-posta gonderilemedi: %s -> %s", subject, to)


def _site(path):
    return settings.SITE_URL.rstrip("/") + path


def user_lang(user, fallback=None):
    """Uyenin kayit oldugu dil (profilde saklanir); yoksa verilen ya da varsayilan dil."""
    try:
        code = user.profile.lang
    except Exception:
        code = ""
    return code or fallback or settings.DEFAULT_LANG


def event_mail(event, lang, to, name, cta_path, extra_paras=(), **fmt):
    """Logolu, 10 dilli olay e-postasi. cta_path /dil-oneki olmadan verilir (orn. /panel/)."""
    if not to:
        return
    from .mail_i18n import EVENTS, WELCOME, html_mail, pick
    table = EVENTS[event]
    subject, paras, cta = pick(table, lang)
    fmt = dict(fmt, name=name)
    subject = subject.format(**fmt)
    paras = [p.format(**fmt) for p in paras] + list(extra_paras)
    code = lang if lang in table else "en"
    url = _site(f"/{code}{cta_path}")
    foot = pick(WELCOME, lang)["foot"]
    text = "\n\n".join(paras + [f"{cta}: {url}", foot])
    _send(subject, text, to, html_mail(paras, cta, url, foot))


# ---------------------------------------------------------------------------
# Magaza basvurusu
# ---------------------------------------------------------------------------
def notify_application_received(application, lang=None):
    user = application.applicant
    event_mail("shop_received", lang or user_lang(user), application.email, application.contact_name or user.username,
               "/panel/", shop=application.shop_name)


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
    user = application.applicant
    event_mail("shop_approved", user_lang(user), application.email, application.contact_name or user.username,
               "/panel/urun/yeni/", shop=shop.name)


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
    lines = [f"{it.title} × {it.qty} — € {it.line_total_eur:.0f}" for it in order.items.all()]
    lines.append(f"€ {order.total_eur:.0f}")
    user = order.buyer
    event_mail("order_paid", user_lang(user), user.email, order.full_name or user.username, "/siparislerim/",
               extra_paras=["\n".join(lines)], n=order.pk)


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


def welcome_user(user, lang=None):
    """Hos geldin e-postasi: uyenin dilinde, logolu, 'ilk ilanini ver' dugmeli."""
    from .models import UserProfile
    lang = lang or settings.DEFAULT_LANG
    try:
        prof, _ = UserProfile.objects.get_or_create(user=user)
        if prof.lang != lang:
            prof.lang = lang
            prof.save(update_fields=["lang"])
    except Exception:
        log.exception("Dil kaydedilemedi")
    if not user.email:
        return
    from .mail_i18n import WELCOME, html_mail, pick
    t = pick(WELCOME, lang)
    name = user.first_name or user.username
    code = lang if lang in WELCOME else "en"
    cta_url = _site(f"/{code}/ilanlarim/yeni/")
    paras = [t["hello"].format(name=name), t["p1"], t["p2"], t["p3"]]
    text = "\n\n".join(paras + [f"{t['cta']}: {cta_url}", t["foot"]])
    _send(t["subject"], text, user.email, html_mail(paras, t["cta"], cta_url, t["foot"]))


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


def _listing_owner_email(listing):
    owner = listing.owner or (listing.shop.owner if listing.shop_id else None)
    return (owner.email, owner) if owner and owner.email else (None, owner)


def notify_listing_received(listing, lang=None):
    to, owner = _listing_owner_email(listing)
    if not to:
        return
    event_mail("listing_received", lang or user_lang(owner), to, owner.first_name or owner.username,
               "/ilanlarim/", title=listing.title)


def notify_listing_approved(listing):
    to, owner = _listing_owner_email(listing)
    if not to:
        return
    event_mail("listing_approved", user_lang(owner), to, owner.first_name or owner.username,
               f"/ilan/{listing.pk}/{listing.slug}/", title=listing.title)


def notify_listing_rejected(listing, reason=""):
    to, _ = _listing_owner_email(listing)
    if not to:
        return
    extra = f"\nNot: {reason}\n" if reason else ""
    _send(f"[Balkan Baazar] Ilanin yayinlanmadi: {listing.title}",
          f"Merhaba,\n\n\"{listing.title}\" ilanin inceleme sonucunda yayinlanmadi.{extra}\n"
          "Duzeltip yeniden ilan verebilirsin.\n\n— Balkan Baazar\n\n---\n\n"
          f"Your listing \"{listing.title}\" was not approved.{extra}\nYou can fix it and post again.\n\n— Balkan Baazar", [to])


def verification_link(user):
    from django.core import signing
    token = signing.dumps({"u": user.pk, "e": user.email}, salt="bb-verify")
    return _site(f"/uyelik/dogrula/{token}/")


def send_verification(user, lang=None):
    if not user.email:
        return
    from .mail_i18n import VERIFY, html_mail, pick
    t = pick(VERIFY, lang or settings.DEFAULT_LANG)
    link = verification_link(user)
    paras = [t["p"]]
    text = "\n\n".join(paras + [f"{t['cta']}: {link}", t["note"]])
    _send(t["subject"], text, user.email, html_mail(paras, t["cta"], link, t["note"]))


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
