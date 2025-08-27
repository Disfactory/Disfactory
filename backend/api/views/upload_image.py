"""
Image upload view for local filesystem storage.

Provides an endpoint that accepts multipart form data and returns
Imgur-compatible JSON responses.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.services.image_upload import ImageUploadService
from .utils import _get_client_ip

LOGGER = logging.getLogger("django")


@swagger_auto_schema(
    method="post",
    operation_summary="上傳圖片文件",
    operation_description="Upload image file to local storage with EXIF processing",
    manual_parameters=[
        openapi.Parameter(
            name="image",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            description="Image file to upload (JPEG, PNG, WEBP)",
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            "Image upload successful",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "link": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="URL to the uploaded image"
                            ),
                            "deletehash": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Hash for potential deletion"
                            ),
                            "Latitude": openapi.Schema(
                                type=openapi.TYPE_NUMBER,
                                description="GPS latitude from EXIF (if available)"
                            ),
                            "Longitude": openapi.Schema(
                                type=openapi.TYPE_NUMBER,
                                description="GPS longitude from EXIF (if available)"
                            ),
                            "DateTimeOriginal": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Original date/time from EXIF (if available)"
                            ),
                        },
                    ),
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "status": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
        ),
        400: openapi.Response(
            "Bad request",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "error": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "status": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
        ),
        413: "Request Entity Too Large",
        500: "Internal Server Error",
    },
    auto_schema=None,
)
@api_view(["POST"])
@csrf_exempt
def upload_image(request):
    """
    Upload image file endpoint.
    
    Accepts multipart form data with 'image' field containing the file.
    Returns Imgur-compatible JSON response with image URL and metadata.
    """
    user_ip = _get_client_ip(request)
    
    # Check if image file is provided
    if 'image' not in request.FILES:
        LOGGER.error(f"upload_image received no image file from {user_ip}")
        return JsonResponse({
            "data": {"error": "No image file provided"},
            "success": False,
            "status": 400
        }, status=400)
    
    uploaded_file = request.FILES['image']
    
    # Check if file is empty
    if not uploaded_file or uploaded_file.size == 0:
        LOGGER.error(f"upload_image received empty file from {user_ip}")
        return JsonResponse({
            "data": {"error": "Empty file provided"},
            "success": False,
            "status": 400
        }, status=400)
    
    LOGGER.info(f"upload_image processing file: {uploaded_file.name} ({uploaded_file.size} bytes) from {user_ip}")
    
    # Process the image
    upload_service = ImageUploadService()
    result = upload_service.process_image(uploaded_file)
    
    # Return response with appropriate status code
    status_code = result.get('status', 200)
    
    if not result.get('success', False):
        LOGGER.error(f"upload_image failed for {user_ip}: {result.get('data', {}).get('error', 'Unknown error')}")
    else:
        LOGGER.info(f"upload_image successful for {user_ip}: {result.get('data', {}).get('link', 'No link')}")
    
    return JsonResponse(result, status=status_code)