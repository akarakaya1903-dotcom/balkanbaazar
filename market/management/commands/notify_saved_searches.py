from django.core.management.base import BaseCommand
from django.db.models import Q
from django.http import QueryDict
from django.utils import timezone

from market import attributes as A
from market import emails, push
from market.models import Category, Listing, SavedSearch


class Command(BaseCommand):
    help = "Kayitli aramalara uyan yeni ilanlari e-posta ve anlik bildirimle haber verir."

    def handle(self, *args, **options):
        now = timezone.now()
        sent = 0
        for ss in SavedSearch.objects.select_related("user", "country"):
            p = QueryDict(ss.params)
            mode = p.get("mode") or ss.mode
            qs = Listing.objects.filter(mode=mode, is_active=True, created_at__gt=ss.last_checked).exclude(owner=ss.user)
            if ss.country_id:
                qs = qs.filter(country_id=ss.country_id)
            root = None
            if p.get("cat"):
                root = Category.objects.filter(mode=mode, parent__isnull=True, slug=p["cat"]).first()
                if root:
                    sub = Category.objects.filter(parent=root, slug=p.get("sub")).first() if p.get("sub") else None
                    qs = qs.filter(category=sub) if sub else qs.filter(Q(category=root) | Q(category__parent=root))
            if p.get("q"):
                qs = A.apply_text(qs, p["q"])
            qs = A.apply_extra(qs, p)
            if p.get("city"):
                qs = qs.filter(city__name=p["city"])
            if p.get("cond") in {"new", "used"}:
                qs = qs.filter(condition=p["cond"])
            if p.get("deliv") in {"ship", "hand"}:
                qs = qs.filter(delivery=p["deliv"])
            rate = float(ss.country.rate_per_eur) if ss.country_id else 1.0
            try:
                if p.get("min"):
                    qs = qs.filter(price_eur__gte=float(p["min"]) / rate)
                if p.get("max"):
                    qs = qs.filter(price_eur__lte=float(p["max"]) / rate)
            except ValueError:
                pass
            if root:
                qs = A.apply_filters(qs, root.slug, p)
            count = qs.count()
            ss.last_checked = now
            ss.save(update_fields=["last_checked"])
            if count:
                new = list(qs.order_by("-created_at")[:5])
                emails.notify_saved_search(ss, new, count)
                push.notify_user(ss.user, ss.label, f"{count} yeni ilan", url="/ilanlar/?" + ss.params, tag=f"ss-{ss.pk}")
                sent += 1
        self.stdout.write(self.style.SUCCESS(f"{sent} kayitli arama icin bildirim gonderildi."))
