"""Standart kutuphane ile TOTP (RFC 6238): Google Authenticator, Microsoft Authenticator, Authy uyumlu."""
import base64
import hashlib
import hmac
import os
import struct
import time

STEP = 30
DIGITS = 6


def new_secret():
    return base64.b32encode(os.urandom(20)).decode()  # 160 bit, 32 karakter


def _code(secret, step):
    key = base64.b32decode(secret, casefold=True)
    h = hmac.new(key, struct.pack(">Q", step), hashlib.sha1).digest()
    o = h[-1] & 0x0F
    n = (struct.unpack(">I", h[o:o + 4])[0] & 0x7FFFFFFF) % (10 ** DIGITS)
    return f"{n:0{DIGITS}d}"


def verify(secret, code, last_step=0, now=None):
    """Kod dogruysa kullanilan adimi (int), degilse None dondurur. Ayni kod ikinci kez kabul edilmez."""
    code = "".join(ch for ch in str(code) if ch.isdigit())
    if len(code) != DIGITS:
        return None
    current = int((now if now is not None else time.time()) // STEP)
    for step in (current - 1, current, current + 1):  # +-30 sn saat farki payi
        if step > last_step and hmac.compare_digest(_code(secret, step), code):
            return step
    return None


def provisioning_uri(secret, account, issuer="Balkan Baazar"):
    from urllib.parse import quote
    return (f"otpauth://totp/{quote(issuer)}:{quote(account)}?secret={secret}"
            f"&issuer={quote(issuer)}&algorithm=SHA1&digits={DIGITS}&period={STEP}")


def pretty(secret):
    return " ".join(secret[i:i + 4] for i in range(0, len(secret), 4))
