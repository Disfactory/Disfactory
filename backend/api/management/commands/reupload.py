import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from api.models import Image
from api.tasks import upload_image


class Command(BaseCommand):
    help = "re-upload images that don't have a Imgur uri"

    def handle(self, *args, **options):
        for img in Image.objects.all():
            if "https://i.imgur.com" not in img.image_path:
                image_path_on_server = os.path.join(
                    settings.MEDIA_ROOT,
                    img.image_path.split("/")[-1],
                )
                success = upload_image(
                    image_path_on_server,
                    settings.IMGUR_CLIENT_ID,
                    img.id,
                )
                if not success:
                    raise CommandError(f"Uploading image {img.id} failed.")

        self.stdout.write(self.style.SUCCESS("Successfully uploading all images to imgur"))
