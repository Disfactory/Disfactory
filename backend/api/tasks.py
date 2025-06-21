import os
import logging
from urllib.parse import urljoin
from uuid import uuid4

from django.conf import settings
import requests
import easymap

from .models import Factory, Image
from .services.image_upload import ImageUploadService

LOGGER = logging.getLogger("django")


def _upload_image_to_imgur(image_buffer, client_id):
    """Legacy function for backward compatibility. Use ImageUploadService instead."""
    tmp_path = os.path.join(settings.MEDIA_ROOT, f"{uuid4()}.jpg")
    with open(tmp_path, "wb") as fw:
        fw.write(image_buffer)
    headers = {"Authorization": f"Client-ID {client_id}"}
    resp = requests.post(
        "https://api.imgur.com/3/image",
        data={"image": image_buffer},
        headers=headers,
    )
    try:
        resp_data = resp.json()
        if "errors" in resp_data:
            credit_resp = requests.get(
                "https://api.imgur.com/3/credits",
                headers=headers,
            )
            LOGGER.error(f"Error upload to imgur. The credits remaining: {credit_resp.json()}")
            path = urljoin(
                urljoin(settings.DOMAIN, settings.MEDIA_URL), os.path.basename(tmp_path)
            )
        else:
            path = resp_data["data"]["link"]
    except Exception:
        LOGGER.error(f"Error parsing imgur response data: {resp_data}")
        path = urljoin(urljoin(settings.DOMAIN, settings.MEDIA_URL), os.path.basename(tmp_path))
    return path


def _upload_image_with_service(image_buffer):
    """Upload image using the new multi-backend service."""
    service = ImageUploadService()
    result = service.upload_image(image_buffer)
    
    if result["success"]:
        return result["url"], result.get("delete_hash")
    else:
        LOGGER.error(f"Image upload failed: {result['error']}")
        # Create local fallback manually as last resort
        try:
            tmp_path = os.path.join(settings.MEDIA_ROOT, f"{uuid4()}.jpg")
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            with open(tmp_path, "wb") as fw:
                fw.write(image_buffer)
            fallback_url = urljoin(
                urljoin(settings.DOMAIN, settings.MEDIA_URL), 
                os.path.basename(tmp_path)
            )
            return fallback_url, None
        except Exception as e:
            LOGGER.error(f"Failed to create local fallback: {e}")
            raise Exception(f"All image upload methods failed: {result['error']}")


def update_landcode(factory_id):
    update_landcode_with_custom_factory_model(factory_id, Factory)


def update_landcode_with_custom_factory_model(factory_id, factory_model):
    factory = factory_model.objects.get(pk=factory_id)
    try:
        landinfo = easymap.get_land_number(lng=factory.lng, lat=factory.lat)
        landcode = landinfo.get("landno")

        LOGGER.info(f"Factory {factory_id} retrieved land number {landcode}")
        factory_model.objects.filter(pk=factory_id).update(
            landcode=landcode,
            sectcode=landinfo.get("sectno"),
            sectname=landinfo.get("sectname"),
            towncode=landinfo.get("towncode"),
            townname=landinfo.get("townname"),
        )
    except Exception as e:
        LOGGER.error(f"update_landcode task failed.")
        LOGGER.error(e)


def upload_image(image_path, client_id, image_id):
    """Upload image using the new multi-backend service."""
    LOGGER.info(f"Upload {image_id}: {image_path}")
    try:
        with open(image_path, "rb") as f:
            image_buffer = f.read()

        # Use new multi-backend service instead of Imgur-only
        path, delete_hash = _upload_image_with_service(image_buffer)
        
        try:
            # Update both image_path and deletehash
            update_data = {"image_path": path}
            if delete_hash:
                update_data["deletehash"] = delete_hash
            Image.objects.filter(pk=image_id).update(**update_data)
        except Exception:
            LOGGER.error(
                f"""
                Upload success and get image url {path},
                but other error happened when update image {image_id}
            """
            )
            return False
    except Exception as e:
        LOGGER.error(f"Upload {image_path} failed: {e}")
        return False

    try:
        os.remove(image_path)
    except Exception:
        LOGGER.warning(
            f"""
            {image_id} upload and write to DB success,
            but other error happened when removing tempfile {image_path}.
        """
        )
        return True

    return True
