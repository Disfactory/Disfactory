from datetime import datetime, timezone, timedelta

import pytest
from freezegun import freeze_time

from api.models import Image


@pytest.mark.django_db
def test_post_image_url(client):
    fake_url = "https://i.imgur.com/123456.png"
    fake_lat = 23.12
    fake_lng = 121.5566
    fake_datetime_str = "2020:03:21 12:33:59"
    fake_datetime = datetime.strptime(
        fake_datetime_str,
        "%Y:%m:%d %H:%M:%S",
    ).replace(tzinfo=timezone(timedelta(hours=8)))
    fake_deletehash = "asdjiwenvnxcvj;"
    request_body = {
        "url": fake_url,
        "Latitude": fake_lat,
        "Longitude": fake_lng,
        "DateTimeOriginal": fake_datetime_str,
        "deletehash": fake_deletehash,
    }
    test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone(timedelta(hours=8)))
    with freeze_time(test_time):
        resp = client.post(
            "/api/images",
            data=request_body,
            content_type="application/json",
        )
    assert resp.status_code == 200

    resp_data = resp.json()
    img_id = resp_data["token"]
    img = Image.objects.get(pk=img_id)
    assert img.image_path == fake_url
    assert img.created_at == test_time
    assert img.orig_time == fake_datetime
    assert img.orig_lat == fake_lat
    assert img.orig_lng == fake_lng


@pytest.mark.django_db
def test_post_image_url_400_if_no_url(client):
    fake_lat = 23.12
    fake_lng = 121.5566
    fake_datetime_str = "2020:03:21 12:33:59"
    fake_deletehash = "asdjiwenvnxcvj;"
    request_body = {
        "Latitude": fake_lat,
        "Longitude": fake_lng,
        "DateTimeOriginal": fake_datetime_str,
        "deletehash": fake_deletehash,
    }
    test_time = datetime(2019, 11, 11, 11, 11, 11, tzinfo=timezone(timedelta(hours=8)))
    with freeze_time(test_time):
        resp = client.post(
            "/api/images",
            data=request_body,
            content_type="application/json",
        )

    assert resp.status_code == 400
