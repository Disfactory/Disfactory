import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from api.models import Image
from api.tasks import upload_image


class Command(BaseCommand):
    help = "Re-upload images using the multi-backend image upload service"

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-upload all images, even those already hosted externally',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )

    def handle(self, *args, **options):
        force = options['force']
        dry_run = options['dry_run']
        
        # Find images that need re-uploading
        if force:
            images_to_upload = Image.objects.all()
            self.stdout.write(f"Force mode: Re-uploading all {images_to_upload.count()} images")
        else:
            # Only re-upload local images (not external URLs)
            images_to_upload = Image.objects.filter(
                image_path__startswith=settings.DOMAIN
            ).exclude(
                image_path__contains="imgur.com"
            ).exclude(
                image_path__contains="ibb.co"
            )
            self.stdout.write(f"Found {images_to_upload.count()} local images to re-upload")
        
        if dry_run:
            self.stdout.write("DRY RUN - No actual uploads will be performed")
            for img in images_to_upload:
                self.stdout.write(f"Would upload: {img.id} - {img.image_path}")
            return
        
        success_count = 0
        error_count = 0
        
        for img in images_to_upload:
            self.stdout.write(f"Processing image {img.id}: {img.image_path}")
            
            # Determine local file path
            if img.image_path.startswith(settings.DOMAIN):
                # Local file - extract filename
                filename = img.image_path.split("/")[-1]
                image_path_on_server = os.path.join(settings.MEDIA_ROOT, filename)
            else:
                # External URL - skip in non-force mode
                if not force:
                    self.stdout.write(f"  Skipping external URL: {img.image_path}")
                    continue
                    
                # In force mode, we'd need to download first
                self.stdout.write(f"  Cannot re-upload external URL in force mode: {img.image_path}")
                error_count += 1
                continue
            
            # Check if local file exists
            if not os.path.exists(image_path_on_server):
                self.stdout.write(f"  ERROR: Local file not found: {image_path_on_server}")
                error_count += 1
                continue
            
            # Upload using new multi-backend service
            success = upload_image(
                image_path_on_server,
                None,  # client_id no longer needed
                img.id,
            )
            
            if success:
                # Reload to see updated URL
                img.refresh_from_db()
                self.stdout.write(f"  SUCCESS: Uploaded to {img.image_path}")
                success_count += 1
            else:
                self.stdout.write(f"  ERROR: Upload failed for image {img.id}")
                error_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Upload completed: {success_count} successful, {error_count} failed"
            )
        )
        
        if error_count > 0:
            raise CommandError(f"Some uploads failed ({error_count} errors)")
