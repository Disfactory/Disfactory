import os
from django.core.management.base import BaseCommand
from api.services.image_upload import ImageUploadService


class Command(BaseCommand):
    help = "Test the image upload service with available backends"

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-file',
            type=str,
            help='Path to test image file (optional)',
        )

    def handle(self, *args, **options):
        self.stdout.write("Testing Image Upload Service...")
        
        # Initialize service
        service = ImageUploadService()
        
        # Show configured backends
        self.stdout.write(f"Configured backends: {len(service.backends)}")
        for backend in service.backends:
            self.stdout.write(f"  - {backend.get_name()}")
        
        # Test with a sample image if provided
        test_file = options.get('test_file')
        if test_file:
            if not os.path.exists(test_file):
                self.stdout.write(
                    self.style.ERROR(f"Test file not found: {test_file}")
                )
                return
                
            self.stdout.write(f"Testing upload with file: {test_file}")
            
            try:
                with open(test_file, 'rb') as f:
                    image_data = f.read()
                
                result = service.upload_image(image_data)
                
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Upload successful!\n"
                            f"  Backend: {result['backend_used']}\n"
                            f"  URL: {result['url']}\n"
                            f"  Delete hash: {result.get('delete_hash', 'N/A')}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Upload failed: {result['error']}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error reading test file: {e}")
                )
        else:
            self.stdout.write("Use --test-file to test actual upload")
            
        self.stdout.write("Test complete")