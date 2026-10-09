"""Admin'den yuklenmis buyuk banner / ana sayfa gorsellerini kucultur (bir kez calistirmak yeter)."""
import os

from django.core.management.base import BaseCommand

from market.models import Banner, SiteSettings, _shrink


def _redo(obj, field, max_side, quality, out):
    f = getattr(obj, field)
    if not f:
        return
    try:
        before = f.size
    except Exception:
        return
    if before < 250 * 1024:
        return
    new = _shrink(f, max_side=max_side, quality=quality)
    if new is f or new.size >= before:
        return
    base = os.path.splitext(os.path.basename(f.name))[0]
    f.save(base + ".jpg", new, save=False)
    out.append((field, before, new.size))


class Command(BaseCommand):
    help = "Buyuk banner/hero gorsellerini kucultur"

    def handle(self, *args, **options):
        done = []
        ss = SiteSettings.objects.first()
        if ss:
            _redo(ss, "hero_image", 1920, 76, done)
            SiteSettings.objects.filter(pk=ss.pk).update(hero_image=ss.hero_image.name if ss.hero_image else "")
        for b in Banner.objects.all():
            _redo(b, "image", 1920, 78, done)
            _redo(b, "image_mobile", 900, 78, done)
            Banner.objects.filter(pk=b.pk).update(image=b.image.name, image_mobile=(b.image_mobile.name if b.image_mobile else None))
        for field, a, b in done:
            self.stdout.write(f"{field}: {a // 1024} KB -> {b // 1024} KB")
        self.stdout.write(f"kucultulen: {len(done)}")
