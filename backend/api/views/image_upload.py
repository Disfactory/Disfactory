"""
Filesystem-based image upload endpoint.

This endpoint provides an Imgur API-compatible response format
so the frontend can switch between Imgur and local storage
by just changing the upload URL.
"""

import hashlib
import logging
import os
import uuid
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .utils import _get_client_ip

LOGGER = logging.getLogger("django")

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def _generate_deletehash(filename: str) -> str:
    """Generate a deletehash for the uploaded image."""
    unique_str = f"{filename}{datetime.now().isoformat()}{uuid.uuid4()}"
    return hashlib.sha256(unique_str.encode()).hexdigest()[:16]


def _get_file_extension(filename: str) -> str:
    """Get the file extension from filename."""
    if "." in filename:
        return "." + filename.rsplit(".", 1)[1].lower()
    return ""


def _is_allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    ext = _get_file_extension(filename)
    return ext in ALLOWED_EXTENSIONS


def _save_uploaded_image(uploaded_file):
    """
    Save the uploaded image to the filesystem.

    Returns a tuple of (saved_filename, deletehash) or raises an exception.
    """
    original_filename = uploaded_file.name
    ext = _get_file_extension(original_filename)

    # Generate a unique filename using UUID
    unique_filename = f"{uuid.uuid4()}{ext}"

    # Create uploads subdirectory if it doesn't exist
    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # Full path for the file
    file_path = os.path.join(upload_dir, unique_filename)

    # Save the file
    with open(file_path, "wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    # Generate deletehash
    deletehash = _generate_deletehash(unique_filename)

    return unique_filename, deletehash


@swagger_auto_schema(
    method="post",
    operation_summary="Upload image to filesystem (Imgur API compatible)",
    manual_parameters=[
        openapi.Parameter(
            "image",
            openapi.IN_FORM,
            description="Image file to upload",
            type=openapi.TYPE_FILE,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            "Image uploaded successfully (Imgur API compatible format)",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "link": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="URL to the uploaded image",
                            ),
                            "deletehash": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Hash for image deletion",
                            ),
                        },
                    ),
                    "success": openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description="Whether the upload was successful",
                    ),
                    "status": openapi.Schema(
                        type=openapi.TYPE_INTEGER, description="HTTP status code"
                    ),
                },
            ),
        ),
        400: "Bad request - invalid file or missing image",
        413: "File too large",
    },
)
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    """
    Upload an image to the filesystem.

    Returns an Imgur API-compatible response format:
    {
        "data": {
            "link": "https://api.disfactory.tw/media/uploads/abc123.jpg",
            "deletehash": "abc123def456"
        },
        "success": true,
        "status": 200
    }
    """
    user_ip = _get_client_ip(request)

    # Check if image file is present
    if "image" not in request.FILES:
        LOGGER.warning(f"upload_image: No image file provided from {user_ip}")
        return JsonResponse(
            {
                "data": {"error": "No image file provided"},
                "success": False,
                "status": 400,
            },
            status=400,
        )

    uploaded_file = request.FILES["image"]

    # Validate file extension
    if not _is_allowed_file(uploaded_file.name):
        LOGGER.warning(
            f"upload_image: Invalid file type {uploaded_file.name} from {user_ip}"
        )
        return JsonResponse(
            {
                "data": {
                    "error": f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                },
                "success": False,
                "status": 400,
            },
            status=400,
        )

    # Validate file size
    if uploaded_file.size > MAX_FILE_SIZE:
        LOGGER.warning(
            f"upload_image: File too large ({uploaded_file.size} bytes) from {user_ip}"
        )
        return JsonResponse(
            {
                "data": {
                    "error": f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB"
                },
                "success": False,
                "status": 413,
            },
            status=413,
        )

    try:
        # Save the file
        filename, deletehash = _save_uploaded_image(uploaded_file)

        # Build the URL
        # Use DOMAIN setting if available, otherwise construct from request
        domain = getattr(settings, "DOMAIN", None)
        if domain:
            # Ensure domain doesn't end with slash
            domain = domain.rstrip("/")
            image_url = f"{domain}{settings.MEDIA_URL}uploads/{filename}"
        else:
            # Fallback: construct from request
            scheme = "https" if request.is_secure() else "http"
            host = request.get_host()
            image_url = f"{scheme}://{host}{settings.MEDIA_URL}uploads/{filename}"

        LOGGER.info(f"upload_image: Successfully uploaded {filename} from {user_ip}")

        # Return Imgur API-compatible response
        return JsonResponse(
            {
                "data": {
                    "link": image_url,
                    "deletehash": deletehash,
                },
                "success": True,
                "status": 200,
            }
        )

    except Exception as e:
        LOGGER.error(f"upload_image: Failed to save image from {user_ip}: {str(e)}")
        return JsonResponse(
            {
                "data": {"error": "Failed to save image"},
                "success": False,
                "status": 500,
            },
            status=500,
        )
