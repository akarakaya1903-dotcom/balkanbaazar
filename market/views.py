from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Case, Count, F, IntegerField, Q, When
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.text import slugify

from .i18n import T
from . import attributes as ATTR
from .models import Banner, Page, Category, City, Country, Favorite, Listing, Mode, Shop


def _current(request):
    lang = getattr(request, "lang_override", None) or request.session.get("lang", settings.DEFAULT_LANG)
    code = request.session.get("country", settings.DEFAULT_COUNTRY)
    country = Country.objects.filter(code=code).first() or Country.objects.first()
    return lang, country


def _back(request, fallback="/"):
    return HttpResponseRedirect(request.META.get("HTTP_REFERER") or fallback)


def set_country(request, code):
    if Country.objects.filter(code=code, is_active=True).exists():
        request.session["country"] = code
    return _back(request)


def set_lang(request, code):
    if code in T:
        request.session["lang"] = code
    return _back(request)


def set_mode(request, code):
    if code in {Mode.USED, Mode.SHOP}:
        request.session["mode"] = code
    return _back(request, "/ilanlar/")


def _nav_categories(mode, country, count="listings"):
    """Kategori seridi icin: alt kategoriler + secili ulkedeki sayilar."""
    qs = Category.objects.filter(mode=mode, parent__isnull=True).prefetch_related("children")
    if count == "shops":
        return qs.annotate(n=Count("shops", filter=Q(shops__country=country), distinct=True))
    return qs.annotate(
        n=Count("listings", filter=Q(listings__country=country, listings__is_active=True),
                distinct=True)
        + Count("children__listings",
                filter=Q(children__listings__country=country,
                         children__listings__is_active=True), distinct=True)
    )


def home(request):
    lang, country = _current(request)
    used_cats = _nav_categories(Mode.USED, country)
    shop_cats = _nav_categories(Mode.SHOP, country, count="shops")
    stats = []
    for c in Country.objects.filter(is_active=True):
        stats.append({
            "country": c,
            "listings": Listing.objects.filter(country=c, is_active=True).count(),
            "shops": Shop.objects.filter(country=c).count(),
        })
    stats.sort(key=lambda x: -(x["listings"] + x["shops"]))
    ctx = {
        "used_cats": used_cats,
        "shop_cats": shop_cats,
        "country_stats": stats,
        "fresh": Listing.objects.filter(country=country, mode=Mode.USED, is_active=True)
                 .select_related("city", "category")
                 .annotate(boosted=Case(When(featured_until__gte=timezone.now(), then=1),
                                        default=0, output_field=IntegerField()))
                 .order_by("-boosted", "-created_at")[:8],
        "products": Listing.objects.filter(country=country, mode=Mode.SHOP, is_active=True)
                    .select_related("city", "shop")
                    .annotate(boosted=Case(When(featured_until__gte=timezone.now(), then=1),
                                           default=0, output_field=IntegerField()))
                    .order_by("-boosted", "-created_at")[:8],
        "featured_shops": [sh for sh in Shop.objects.filter(country=country).select_related("city")[:24] if sh.product_count][:6],
        "total_listings": Listing.objects.filter(is_active=True).count(),
        "total_shops": Shop.objects.count(),
    }
    ctx["trending"] = _trending_qs(country)[:8]
    return render(request, "market/home.html", ctx)


def _trending_qs(country):
    """Trend skoru = goruntulenme + 5 x favori sayisi."""
    return (Listing.objects.filter(country=country, is_active=True)
            .select_related("city", "shop")
            .annotate(favs=Count("favorited_by", distinct=True))
            .annotate(score=F("views") + F("favs") * 5)
            .order_by("-score", "-created_at"))


def trending(request):
    lang, country = _current(request)
    return render(request, "market/trending.html", {"items": _trending_qs(country)[:48]})


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_published=True)
    from .models import SiteSettings
    lang, _country = _current(request)
    title, body = page.localized(lang)
    ss = SiteSettings.objects.first()
    values = {
        "company": (ss.company_name if ss and ss.company_name else "Balkan Baazar"),
        "address": (ss.address if ss and ss.address else ""),
        "email": (ss.email if ss and ss.email else ""),
        "phone": (ss.phone if ss and ss.phone else ""),
    }
    lines = []
    for line in body.split("\n"):
        skip = False
        for key, val in values.items():
            token = "[[" + key + "]]"
            if token in line:
                if not val:
                    skip = True  # bos bilgiyi iceren satiri gosterme (orn. adres girilmemisse)
                line = line.replace(token, val)
        if not skip:
            lines.append(line)
    return render(request, "market/page.html", {"page": page, "title": title, "body": "\n".join(lines)})


def banner_go(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    Banner.objects.filter(pk=pk).update(clicks=F("clicks") + 1)
    return HttpResponseRedirect(banner.link_url or "/")


def listings(request, _o=None):
    o = _o or {}
    lang, country = _current(request)
    if o.get("country"):
        country = o["country"]
    mode = o.get("mode") or request.GET.get("mode") or request.session.get("mode", Mode.USED)
    if mode not in {Mode.USED, Mode.SHOP}:
        mode = Mode.USED
    request.session["mode"] = mode

    qs = (Listing.objects.filter(mode=mode, country=country, is_active=True)
          .select_related("city", "category", "category__parent", "shop")
          .annotate(boosted=Case(
              When(featured_until__gte=timezone.now(), then=1),
              default=0, output_field=IntegerField(),
          )))

    cat_slug = o.get("cat") or request.GET.get("cat") or ""
    sub_slug = o.get("sub") or request.GET.get("sub") or ""
    root = None
    sub = None
    if cat_slug:
        root = Category.objects.filter(mode=mode, parent__isnull=True, slug=cat_slug).first()
        if root:
            if sub_slug:
                sub = Category.objects.filter(parent=root, slug=sub_slug).first()
            qs = qs.filter(category=sub) if sub else qs.filter(
                Q(category=root) | Q(category__parent=root)
            )

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    city = o.get("city") or request.GET.get("city", "")
    if city:
        qs = qs.filter(city__name=city)
    cond = request.GET.get("cond", "")
    if cond in {"new", "used"}:
        qs = qs.filter(condition=cond)
    deliv = request.GET.get("deliv", "")
    if deliv in {"ship", "hand"}:
        qs = qs.filter(delivery=deliv)
    rate = float(country.rate_per_eur) if country else 1.0
    pmin, pmax = request.GET.get("min", ""), request.GET.get("max", "")
    try:
        if pmin:
            qs = qs.filter(price_eur__gte=float(pmin) / rate)
        if pmax:
            qs = qs.filter(price_eur__lte=float(pmax) / rate)
    except ValueError:
        pmin = pmax = ""

    if root:
        qs = ATTR.apply_filters(qs, root.slug, request.GET)
    sort = request.GET.get("sort", "new")
    secondary = {
        "lo": "price_eur", "hi": "-price_eur", "pop": "-favorites",
    }.get(sort, "-created_at")
    qs = qs.order_by("-boosted", secondary)

    page = Paginator(qs, 24).get_page(request.GET.get("page"))

    roots = _nav_categories(mode, country)
    subs = []
    if root:
        subs = (Category.objects.filter(parent=root)
                .annotate(n=Count("listings", filter=Q(listings__country=country)))
                .order_by("order"))

    ctx = {
        "mode": mode, "page_obj": page, "roots": roots, "subs": subs,
        "nav_cats": roots, "nav_base": "/ilanlar/?mode=" + mode, "nav_sep": "&",
        "nav_mode": mode,
        "root": root, "sub": sub, "cities": City.objects.filter(country=country),
        "f": {"q": q, "city": city, "cond": cond, "deliv": deliv,
              "min": pmin, "max": pmax, "sort": sort},
        "featured_shops": Shop.objects.filter(country=country,
                                              **({"category": root} if root else {}))[:4]
        if mode == Mode.SHOP else [],
        "total": page.paginator.count,
        "seo": o.get("seo"),
        "attr_specs": ATTR.filter_specs(root.slug, request.GET, lang) if root else [],
        "attr_pairs": ATTR.param_pairs(root.slug, request.GET) if root else [],
    }
    from urllib.parse import urlencode as _ue
    _p = {"mode": mode, "cat": cat_slug if root else "", "sub": sub_slug if sub else "", "city": city, "q": q,
          "cond": cond, "deliv": deliv, "min": pmin, "max": pmax}
    _p = {k: v for k, v in _p.items() if v}
    _p.update(dict(ctx["attr_pairs"]))
    ctx["search_qs"] = _ue(_p)
    ctx["search_label"] = " · ".join(x for x in [
        ((sub or root).name(lang) if root else ""), city, q] if x) or ("Tüm ilanlar" if mode == Mode.USED else "Tüm ürünler")
    return render(request, "market/listings.html", ctx)


def listing_detail(request, pk, slug):
    lang, country = _current(request)
    item = get_object_or_404(
        Listing.objects.select_related("country", "city", "category", "shop"), pk=pk
    )
    Listing.objects.filter(pk=pk).update(views=item.views + 1)
    similar = (Listing.objects.filter(mode=item.mode, category=item.category,
                                      country=item.country, is_active=True)
               .exclude(pk=item.pk)[:8])
    is_fav = (request.user.is_authenticated
              and Favorite.objects.filter(user=request.user, listing=item).exists())
    return render(request, "market/listing_detail.html",
                  {"item": item, "similar": similar, "is_fav": is_fav})


def shops(request):
    lang, country = _current(request)
    qs = Shop.objects.filter(country=country).select_related("city", "category")
    cat_slug = request.GET.get("cat", "")
    root = None
    if cat_slug:
        root = Category.objects.filter(mode=Mode.SHOP, parent__isnull=True, slug=cat_slug).first()
        if root:
            qs = qs.filter(category=root)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(name__icontains=q)
    page = Paginator(qs, 24).get_page(request.GET.get("page"))
    nav = _nav_categories(Mode.SHOP, country, count="shops")
    return render(request, "market/shops.html", {
        "page_obj": page, "roots": nav, "nav_cats": nav,
        "nav_base": "/magazalar/?", "nav_sep": "", "nav_mode": Mode.SHOP,
        "root": root, "f": {"q": q}, "total": page.paginator.count,
        "shop_categories": nav,
    })


def shop_detail(request, slug):
    shop = get_object_or_404(Shop.objects.select_related("country", "city", "category"), slug=slug)
    page = Paginator(shop.listings.filter(is_active=True), 24).get_page(request.GET.get("page"))
    return render(request, "market/shop_detail.html", {"shop": shop, "page_obj": page})


def pricing(request):
    return render(request, "market/pricing.html", {
        "free_months": settings.SHOP_PLAN_FREE_MONTHS,
        "mid_price": settings.SHOP_PLAN_MID_PRICE_EUR,
        "mid_until": settings.SHOP_PLAN_MID_UNTIL_MONTH,
        "full_price": settings.SHOP_PLAN_FULL_PRICE_EUR,
    })


def _city_by_slug(city_slug):
    for c in City.objects.select_related("country"):
        if slugify(c.name) == city_slug:
            return c
    return None


def seo_listing(request, mode, cat, sub=None, city=None):
    """Arama motoru icin temiz adresli kategori / sehir sayfalari."""
    if mode not in {Mode.USED, Mode.SHOP}:
        raise Http404
    root = Category.objects.filter(mode=mode, parent__isnull=True, slug=cat).first()
    if not root:  # bilinmeyen kategori: eski liste sayfasina don (404 yerine)
        from django.urls import reverse
        return HttpResponseRedirect(reverse("market:listings") + f"?mode={mode}&cat={cat}")
    subcat = get_object_or_404(Category, parent=root, slug=sub) if sub else None
    lang, country = _current(request)
    override = {"mode": mode, "cat": cat, "sub": sub or ""}
    city_obj = None
    if city:
        city_obj = _city_by_slug(city)
        if not city_obj:
            raise Http404
        override["city"] = city_obj.name
        override["country"] = city_obj.country
        country = city_obj.country
    t = T.get(lang) or T["en"]
    cat_name = (subcat or root).name(lang)
    mode_label = t.get("used", "") if mode == Mode.USED else t.get("shops", "")
    place = city_obj.name if city_obj else (country.name_local if country else "")
    title = f"{cat_name} · {mode_label} · {place} — {t.get('brand', 'Balkan Baazar')}"
    desc = f"{cat_name} — {mode_label}, {place}. {t.get('heroP', '')}"[:160]
    override["seo"] = {"title": title, "description": desc, "h1": f"{cat_name} · {mode_label} · {place}"}
    return listings(request, override)
