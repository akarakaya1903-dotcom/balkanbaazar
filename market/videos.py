"""Yuklenen videolari sunucuda otomatik kucultme (FFmpeg gerekir: apt install ffmpeg)."""
import os
import shutil
import subprocess
import sys


def have_ffmpeg():
    return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def probe_duration(path):
    """Videonun suresi (saniye); okunamazsa None."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path],
            capture_output=True, text=True, timeout=60)
        return float(out.stdout.strip())
    except Exception:
        return None


def compress(src, dst, max_side=1280, crf=29):
    """720p'ye kadar kucultur, H.264/AAC mp4 uretir. Basariliysa True."""
    vf = (f"scale='min({max_side},iw)':'min({max_side},ih)':force_original_aspect_ratio=decrease,"
          "scale=trunc(iw/2)*2:trunc(ih/2)*2")
    cmd = ["nice", "-n", "10", "ffmpeg", "-y", "-i", src, "-vf", vf,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", "-max_muxing_queue_size", "1024", dst]
    if not shutil.which("nice"):
        cmd = cmd[3:]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60 * 60)
    except Exception:
        return False
    return r.returncode == 0 and os.path.exists(dst) and os.path.getsize(dst) > 0


def start_video_job(listing):
    """Kayit sonrasi kucultmeyi arka planda baslatir (istegi bekletmez)."""
    try:
        if not (listing.video and not listing.video_processed):
            return
        from django.conf import settings
        subprocess.Popen(
            [sys.executable, str(settings.BASE_DIR / "manage.py"), "compress_videos", "--id", str(listing.pk)],
            cwd=str(settings.BASE_DIR), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True, env=os.environ.copy())
    except Exception:
        pass
