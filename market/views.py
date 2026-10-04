from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Case, Count, F, IntegerField, Q, When
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .i18n import T
from .models import Banner, Page, Category, City, Country, Favorite, Listing, Mode, Shop


def _current(request):
    lang = request.session.get("lang", settings.DEFAULT_LANG)
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
        "featured_shops": Shop.objects.filter(country=country)[:6],
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
    return render(request, "market/page.html", {"page": page})


def banner_go(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    Banner.objects.filter(pk=pk).update(clicks=F("clicks") + 1)
    return HttpResponseRedirect(banner.link_url or "/")


def listings(request):
    lang, country = _current(request)
    mode = request.GET.get("mode") or request.session.get("mode", Mode.USED)
    if mode not in {Mode.USED, Mode.SHOP}:
        mode = Mode.USED
    request.session["mode"] = mode

    qs = (Listing.objects.filter(mode=mode, country=country, is_active=True)
          .select_related("city", "category", "category__parent", "shop")
          .annotate(boosted=Case(
              When(featured_until__gte=timezone.now(), then=1),
              default=0, output_field=IntegerField(),
          )))

    cat_slug = request.GET.get("cat") or ""
    sub_slug = request.GET.get("sub") or ""
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
    city = request.GET.get("city", "")
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
    }
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
