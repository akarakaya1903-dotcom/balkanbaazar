import fcntl
import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from market import videos
from market.models import Listing


class Command(BaseCommand):
    help = "Yeni yuklenen videolari FFmpeg ile kucultur (720p, H.264). Ayni anda tek islem calisir."

    def add_arguments(self, parser):
        parser.add_argument("--id", type=int, help="Sadece bu ilanin videosunu isle")

    def handle(self, *args, **options):
        if not videos.have_ffmpeg():
            self.stderr.write("ffmpeg bulunamadi. Kur: apt-get install -y ffmpeg")
            return
        old = os.umask(0)
        fd = os.open("/tmp/bb-video.lock", os.O_RDWR | os.O_CREAT, 0o666)
        os.umask(old)
        lock = os.fdopen(fd, "w")
        fcntl.flock(lock, fcntl.LOCK_EX)  # siraya gir, ayni anda tek video islensin
        qs = Listing.objects.exclude(video="").exclude(video__isnull=True).filter(video_processed=False)
        if options.get("id"):
            qs = qs.filter(pk=options["id"])
        for item in qs[:20]:
            src = item.video.path
            if not os.path.exists(src):
                Listing.objects.filter(pk=item.pk).update(video_processed=True)
                continue
            limit = settings.MAX_VIDEO_SECONDS + 15
            dur = videos.probe_duration(src)
            if dur and dur > limit:
                os.remove(src)
                Listing.objects.filter(pk=item.pk).update(video="", video_processed=True)
                self.stdout.write(f"#{item.pk}: video cok uzun ({int(dur)} sn), silindi")
                continue
            stem, _ = os.path.splitext(src)
            dst = stem + "_c.mp4"
            before = os.path.getsize(src)
            if videos.compress(src, dst):
                try:
                    shutil.chown(dst, "www-data", "www-data")
                except Exception:
                    pass
                after = os.path.getsize(dst)
                if after < before:
                    rel = os.path.relpath(dst, settings.MEDIA_ROOT)
                    Listing.objects.filter(pk=item.pk).update(video=rel, video_processed=True)
                    os.remove(src)
                    self.stdout.write(f"#{item.pk}: {before // 1048576} MB -> {after // 1048576} MB")
                else:  # kucultme fayda saglamadi, orijinal kalsin
                    os.remove(dst)
                    Listing.objects.filter(pk=item.pk).update(video_processed=True)
                    self.stdout.write(f"#{item.pk}: zaten kucuk, degismedi")
            else:
                if os.path.exists(dst):
                    os.remove(dst)
                Listing.objects.filter(pk=item.pk).update(video_processed=True)
                self.stdout.write(f"#{item.pk}: kucultme basarisiz, orijinal kaldi")
