"""Google ile giris / uyelik (OAuth 2.0 yetkilendirme kodu akisi)."""
import secrets
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.text import slugify

from . import emails

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
INFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


def _redirect_uri(request):
    """Kullanici hangi adresten geldiyse (www olsun olmasin) ayni adrese doner, oturum korunur."""
    return request.build_absolute_uri(reverse("market:google_callback"))


def google_login(request):
    if not settings.GOOGLE_CLIENT_ID:
        raise Http404
    state = secrets.token_urlsafe(24)
    request.session["g_state"] = state
    query = urlencode({
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": _redirect_uri(request),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    })
    return redirect(f"{AUTH_URL}?{query}")


def google_callback(request):
    if not settings.GOOGLE_CLIENT_ID:
        raise Http404
    expected = request.session.pop("g_state", None)
    if not expected or request.GET.get("state") != expected or "code" not in request.GET:
        messages.error(request, "Google girisi tamamlanamadi, tekrar dene.")
        return redirect("market:login")
    try:
        token = requests.post(TOKEN_URL, data={
            "code": request.GET["code"],
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": _redirect_uri(request),
            "grant_type": "authorization_code",
        }, timeout=10).json()
        info = requests.get(INFO_URL, headers={"Authorization": f"Bearer {token['access_token']}"},
                            timeout=10).json()
    except Exception:
        messages.error(request, "Google ile baglanti kurulamadi.")
        return redirect("market:login")
    email = (info.get("email") or "").strip().lower()
    if not email or not info.get("email_verified"):
        messages.error(request, "Google hesabinin e-postasi dogrulanmamis.")
        return redirect("market:login")
    User = get_user_model()
    user = User.objects.filter(email__iexact=email).first()
    created = False
    if not user:
        base = slugify(email.split("@")[0]) or "uye"
        username, n = base, 1
        while User.objects.filter(username=username).exists():
            username, n = f"{base}{n}", n + 1
        user = User(username=username, email=email,
                    first_name=(info.get("given_name") or "")[:150],
                    last_name=(info.get("family_name") or "")[:150])
        user.set_unusable_password()
        user.save()
        created = True
    from .models import UserProfile
    prof, _ = UserProfile.objects.get_or_create(user=user)
    if not prof.email_verified:
        prof.email_verified = True
        prof.save(update_fields=["email_verified"])
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    if created:
        emails.notify_staff_new_user(user)
        emails.welcome_user(user)
        messages.success(request, "Hesabin hazir.")
    return redirect("market:panel")
