import logging

from django.http import HttpResponse, JsonResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.services.image_upload import get_image_upload_service
from .utils import _get_client_ip

LOGGER = logging.getLogger("django")


@swagger_auto_schema(
    method="post",
    operation_summary="直接上傳圖片檔案",
    manual_parameters=[
        openapi.Parameter(
            'image',
            openapi.IN_FORM,
            description="圖片檔案",
            type=openapi.TYPE_FILE,
            required=True
        ),
    ],
    responses={
        200: openapi.Response(
            "圖片上傳成功",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "url": openapi.Schema(type=openapi.TYPE_STRING, description="image url"),
                },
            ),
        ),
        400: "request failed",
        500: "upload failed",
    },
)
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_image_file(request):
    """
    Upload image file directly to storage service and return URL.
    """
    user_ip = _get_client_ip(request)
    
    # Validate image file
    if 'image' not in request.FILES:
        LOGGER.error(f"upload_image_file received no image file from {user_ip}")
        return HttpResponse("Image file is required", status=400)
    
    image_file: InMemoryUploadedFile = request.FILES['image']
    
    # Validate file type
    if not image_file.content_type or not image_file.content_type.startswith('image/'):
        LOGGER.error(f"upload_image_file received non-image file from {user_ip}: {image_file.content_type}")
        return HttpResponse("File must be an image", status=400)
    
    # Validate file size (limit to 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if image_file.size > max_size:
        LOGGER.error(f"upload_image_file received oversized file from {user_ip}: {image_file.size} bytes")
        return HttpResponse("File size must be less than 10MB", status=400)
    
    LOGGER.info(f"upload_image_file {image_file.name} ({image_file.size} bytes) from {user_ip}")
    
    try:
        # Upload to storage service
        upload_service = get_image_upload_service()
        upload_result = upload_service.upload_image(image_file)
        
        if not upload_result.success:
            LOGGER.error(f"Image upload failed for {user_ip}: {upload_result.error}")
            return HttpResponse(f"Upload failed: {upload_result.error}", status=500)
        
        LOGGER.info(f"Successfully uploaded image to {upload_result.url} from {user_ip}")
        
        return JsonResponse({
            "url": upload_result.url
        })
        
    except Exception as e:
        LOGGER.error(f"Unexpected error during image upload from {user_ip}: {str(e)}")
        return HttpResponse("Internal server error", status=500)