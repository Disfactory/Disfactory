import json
import logging
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.db import transaction
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

from api.models import Image, Factory, ReportRecord
from api.serializers import ImageSerializer
from api.services.image_upload import ImageUploadService
from .utils import _get_client_ip

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

LOGGER = logging.getLogger("django")


@swagger_auto_schema(
    method="post",
    operation_summary="上傳指定 id 的工廠圖片",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "url": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="image url",
            ),
            "deletehash": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="image delete hash",
            ),
            "DateTimeOriginal": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="YYYY:mm:dd HH:MM:SS",
            ),
        },
    ),
    responses={
        200: openapi.Response("圖片資料", ImageSerializer),
        400: "request failed",
    },
    auto_schema=None,
)
@api_view(["POST"])
def post_factory_image_url(request, factory_id):
    user_ip = _get_client_ip(request)

    try:
        post_body = request.data
    except json.JSONDecodeError:
        LOGGER.error(f"post_factory_image_url received non-json body from {user_ip}")
        return HttpResponse("Post body should be JSON", status=400)

    if "url" not in post_body:
        LOGGER.error(f"post_factory_image_url received no url from {user_ip}")
        return HttpResponse("`url` should be in post body", status=400)

    if not Factory.objects.filter(pk=factory_id).exists():
        LOGGER.warning(
            f"post_factory_image_url receiving {factory_id} that does not exist from {user_ip}"
        )
        return HttpResponse(
            f"Factory ID {factory_id} does not exist.",
            status=400,
        )

    img_url = post_body["url"]
    LOGGER.info(f"post_image_url {img_url} from {user_ip}")

    if "DateTimeOriginal" in post_body:
        try:
            orig_time_str = post_body["DateTimeOriginal"]
            orig_time = datetime.strptime(
                orig_time_str,
                "%Y:%m:%d %H:%M:%S",
            )
        except ValueError:
            LOGGER.warning(f"post_image_url cannot parse DateTimeOriginal {orig_time_str}")
            orig_time = None
    else:
        orig_time = None

    with transaction.atomic():
        factory = Factory.objects.only("id").get(pk=factory_id)
        report_record = ReportRecord.objects.create(
            factory=factory,
            action_type="POST_IMAGE",
            action_body={},
            nickname=post_body.get("nickname"),
            contact=post_body.get("contact"),
        )
        image = Image.objects.create(
            image_path=img_url,
            orig_lat=post_body.get("Latitude"),
            orig_lng=post_body.get("Longitude"),
            orig_time=orig_time,
            report_record=report_record,
            factory=factory,
            deletehash=post_body.get("deletehash"),
        )

    img_serializer = ImageSerializer(image)
    return JsonResponse(img_serializer.data, safe=False)


@swagger_auto_schema(
    method="post",
    operation_summary="直接上傳工廠圖片檔案",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "image": openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_BINARY,
                description="image file",
            ),
            "DateTimeOriginal": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="YYYY:mm:dd HH:MM:SS",
            ),
            "Latitude": openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description="GPS latitude",
            ),
            "Longitude": openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description="GPS longitude",
            ),
            "nickname": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Reporter nickname",
            ),
            "contact": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Reporter contact",
            ),
        },
        required=["image"],
    ),
    responses={
        200: openapi.Response("圖片資料", ImageSerializer),
        400: "request failed",
    },
    auto_schema=None,
)
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def post_factory_image_file(request, factory_id):
    """Upload image file directly to backend with multiple provider support."""
    user_ip = _get_client_ip(request)
    
    if not Factory.objects.filter(pk=factory_id).exists():
        LOGGER.warning(
            f"post_factory_image_file receiving {factory_id} that does not exist from {user_ip}"
        )
        return HttpResponse(
            f"Factory ID {factory_id} does not exist.",
            status=400,
        )

    # Check if image file is provided
    if 'image' not in request.FILES:
        LOGGER.error(f"post_factory_image_file received no image file from {user_ip}")
        return HttpResponse("Image file is required", status=400)

    image_file = request.FILES['image']
    LOGGER.info(f"post_factory_image_file received {image_file.name} from {user_ip}")

    # Read image data
    try:
        image_buffer = image_file.read()
        if len(image_buffer) == 0:
            return HttpResponse("Empty image file", status=400)
    except Exception as e:
        LOGGER.error(f"Error reading image file: {e}")
        return HttpResponse("Error reading image file", status=400)

    # Upload image using multi-backend service
    try:
        service = ImageUploadService()
        upload_result = service.upload_image(image_buffer)
        
        if not upload_result["success"]:
            LOGGER.error(f"Image upload failed: {upload_result['error']}")
            return HttpResponse(f"Image upload failed: {upload_result['error']}", status=500)
            
        img_url = upload_result["url"]
        delete_hash = upload_result.get("delete_hash")
        backend_used = upload_result.get("backend_used")
        
        LOGGER.info(f"Image uploaded successfully using {backend_used}: {img_url}")
        
    except Exception as e:
        LOGGER.error(f"Unexpected error during image upload: {e}")
        return HttpResponse(f"Upload service error: {str(e)}", status=500)

    # Parse EXIF datetime if provided
    orig_time = None
    if "DateTimeOriginal" in request.data:
        try:
            orig_time_str = request.data["DateTimeOriginal"]
            orig_time = datetime.strptime(
                orig_time_str,
                "%Y:%m:%d %H:%M:%S",
            )
        except ValueError:
            LOGGER.warning(f"post_factory_image_file cannot parse DateTimeOriginal {orig_time_str}")
            orig_time = None

    # Save to database
    with transaction.atomic():
        factory = Factory.objects.only("id").get(pk=factory_id)
        report_record = ReportRecord.objects.create(
            factory=factory,
            action_type="POST_IMAGE",
            action_body={},
            nickname=request.data.get("nickname"),
            contact=request.data.get("contact"),
        )
        image = Image.objects.create(
            image_path=img_url,
            orig_lat=request.data.get("Latitude"),
            orig_lng=request.data.get("Longitude"),
            orig_time=orig_time,
            report_record=report_record,
            factory=factory,
            deletehash=delete_hash,
        )

    img_serializer = ImageSerializer(image)
    return JsonResponse(img_serializer.data, safe=False)
