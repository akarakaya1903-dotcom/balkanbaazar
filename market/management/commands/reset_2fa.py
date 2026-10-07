from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from market.models import StaffTOTP


class Command(BaseCommand):
    help = "Bir yoneticinin iki adimli dogrulamasini sifirlar (telefon kaybi). Kullanim: manage.py reset_2fa KULLANICI_ADI"

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, *args, **opts):
        try:
            user = get_user_model().objects.get(username=opts["username"])
        except get_user_model().DoesNotExist:
            raise CommandError("Kullanici bulunamadi.")
        n, _ = StaffTOTP.objects.filter(user=user).delete()
        self.stdout.write(self.style.SUCCESS(
            f"{user.username}: 2FA sifirlandi." if n else f"{user.username}: zaten 2FA kaydi yok."))
        self.stdout.write("Bir sonraki yonetici giriste yeni kurulum ekrani acilir.")
