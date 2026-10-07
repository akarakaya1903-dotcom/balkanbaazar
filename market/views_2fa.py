"""Yonetici iki adimli dogrulama sayfasi (kurulum + giris)."""
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from . import totp
from .models import StaffTOTP

MAX_FAILS = 5
LOCK_MINUTES = 15


def _next_url(request):
    nxt = request.POST.get("next") or request.GET.get("next") or "/admin/"
    if url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return nxt
    return "/admin/"


@login_required
def staff_2fa(request):
    if not request.user.is_staff:
        return redirect("/")
    nxt = _next_url(request)
    if settings.STAFF_2FA_DISABLED or request.session.get("bb_2fa_user") == request.user.pk:
        return redirect(nxt)
    device, _ = StaffTOTP.objects.get_or_create(user=request.user, defaults={"secret": totp.new_secret()})
    setup = not device.confirmed
    now = timezone.now()
    locked = bool(device.locked_until and device.locked_until > now)
    error = ""
    if request.method == "POST":
        if locked:
            error = "Cok fazla hatali deneme. Lutfen birkac dakika sonra tekrar dene."
        else:
            step = totp.verify(device.secret, request.POST.get("code", ""), device.last_step)
            if step is None:
                device.failed += 1
                if device.failed >= MAX_FAILS:
                    device.locked_until = now + timedelta(minutes=LOCK_MINUTES)
                    device.failed = 0
                device.save(update_fields=["failed", "locked_until"])
                error = "Kod yanlis veya suresi dolmus. Uygulamadaki guncel 6 haneli kodu gir."
            else:
                device.last_step = step
                device.failed = 0
                device.locked_until = None
                device.confirmed = True
                device.save(update_fields=["last_step", "failed", "locked_until", "confirmed"])
                request.session["bb_2fa_user"] = request.user.pk
                if setup:
                    messages.success(request, "Iki adimli dogrulama kuruldu. Bundan sonra her yonetici girisinde kod istenecek.")
                return redirect(nxt)
    ctx = {"setup": setup, "error": error, "next": nxt, "locked": locked}
    if setup:
        ctx["secret"] = totp.pretty(device.secret)
        ctx["uri"] = totp.provisioning_uri(device.secret, request.user.get_username())
    resp = render(request, "market/account/staff_2fa.html", ctx)
    resp["Cache-Control"] = "no-store"
    return resp
