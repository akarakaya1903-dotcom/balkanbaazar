# -*- coding: utf-8 -*-
"""Fiyati dusen ilani favorisine ekleyenlere e-posta ve anlik bildirim."""
from . import emails, push


def notify_price_drop(listing, old_eur):
    from .models import Favorite
    old, new = listing.old_display_price(), listing.display_price()
    qs = Favorite.objects.filter(listing=listing)
    if listing.owner_id:
        qs = qs.exclude(user_id=listing.owner_id)
    for fav in qs.select_related("user")[:200]:
        user = fav.user
        if user.email:
            emails.event_mail("price_drop", emails.user_lang(user), user.email,
                              user.first_name or user.username, f"/ilan/{listing.pk}/{listing.slug}/",
                              title=listing.title, old=old, new=new)
        push.notify_user(user, listing.title, f"{old} → {new}", url=f"/ilan/{listing.pk}/{listing.slug}/",
                         tag=f"drop-{listing.pk}")
