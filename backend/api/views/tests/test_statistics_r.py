import datetime

import pytest
from freezegun import freeze_time

from ...models import Image, Factory, Document
from ...models.const import DocumentDisplayStatusConst
from ...models.document import DocumentDisplayStatusEnum


pytestmark = pytest.mark.django_db


def update_landcode_with_custom_factory_model(factory_id):
    Factory.objects.filter(pk=factory_id).update(
        landcode="853-2",
        sectcode="5404",
        sectname="溪底寮段三寮灣小段",
        towncode="D24",
        townname="臺北市中山區",
    )


def create_factory(cli):
    lat = 23.234
    lng = 120.1
    others = "這個工廠實在太臭啦，趕緊檢舉吧"
    nickname = "路過的家庭主婦"
    contact = "07-7533967"
    factory_type = "2-3"

    im1 = Image.objects.create(image_path="https://i.imgur.com/RxArJUc.png")
    im2 = Image.objects.create(image_path="https://imgur.dcard.tw/BB2L2LT.jpg")

    request_body = {
        "name": "a new factory",
        "type": factory_type,
        "images": [str(im1.id), str(im2.id)],
        "others": others,
        "lat": lat,
        "lng": lng,
        "nickname": nickname,
        "contact": contact,
    }

    test_time = datetime.datetime(2019, 11, 11, 11, 11, 11, tzinfo=datetime.timezone.utc)
    with freeze_time(test_time):
        resp = cli.post(
            "/api/factories", data=request_body, content_type="application/json"
        )
        data = resp.json()
        update_landcode_with_custom_factory_model(data["id"])
        return data["id"]


def test_get_factory_statistics(client):
    # Create 10 factories in 臺北市中山區
    id_list = []
    for index in range(0, 10):
        result = create_factory(client)
        id_list.append(result)

    resp = client.get("/api/statistics/factories?source=U")
    assert resp.json()["factories"] == 10

    resp = client.get("/api/statistics/factories?source=U&level=city")
    assert resp.json()["cities"]["臺北市"]["factories"] == 10
    assert resp.json()["cities"]["臺南市"]["factories"] == 0

    resp = client.get("/api/statistics/factories?source=G&level=city")
    assert resp.json()["cities"]["臺南市"]["factories"] == 101

    resp = client.get("/api/statistics/factories?townname=台北市")
    assert resp.json()["cities"]["臺北市"]["factories"] == 10

    resp = client.get("/api/statistics/factories?townname=台北市中山區")
    assert resp.json()["cities"]["臺北市"]["towns"]["中山區"]["factories"] == 10

    resp = client.get("/api/statistics/factories?townname=台南市")
    assert resp.json()["cities"]["臺南市"]["factories"] == 101

    resp = client.get(f"/api/statistics/factories?display_status={DocumentDisplayStatusConst.REPORTED}")
    assert resp.json()["factories"] == 0

    # Add a document to factory in 臺北市中山區
    Document.objects.create(
        cet_staff="AAA",
        code="123456",
        factory=Factory.objects.get(id=id_list[0]),
        display_status=0
    )
    resp = client.get("/api/statistics/factories?townname=臺北市")
    assert resp.json()["cities"]["臺北市"]["factories"] == 10
    assert resp.json()["cities"]["臺北市"]["documents"] == 1

    resp = client.get(f"/api/statistics/factories?display_status={DocumentDisplayStatusConst.REPORTED}")
    assert resp.json()["factories"] == 1
    assert resp.json()["documents"] == 1

    resp = client.get(f"/api/statistics/factories?display_status={DocumentDisplayStatusConst.REPORTED}&level=city")
    assert resp.json()["cities"]["臺北市"]["factories"] == 1
    assert resp.json()["cities"]["臺北市"]["documents"] == 1

    resp = client.get(f"/api/statistics/factories?townname=台南市&display_status={DocumentDisplayStatusConst.REPORTED}")
    assert resp.json()["cities"]["臺南市"]["factories"] == 0

    resp = client.get(f"/api/statistics/factories?townname=台北市&display_status={DocumentDisplayStatusConst.REPORTED}")
    assert resp.json()["cities"]["臺北市"]["factories"] == 1
    assert resp.json()["cities"]["臺北市"]["documents"] == 1

    Document.objects.create(
        cet_staff="AAA",
        code="123457",
        factory=Factory.objects.get(id=id_list[0]),
        display_status=1
    )
    resp = client.get(f"/api/statistics/factories?townname=台北市&display_status={DocumentDisplayStatusConst.REPORTED}")
    assert resp.json()["factories"] == 1
    assert resp.json()["cities"]["臺北市"]["factories"] == 1

    resp = client.get(f"/api/statistics/factories?townname=台北市&display_status={DocumentDisplayStatusConst.AUDIT_SCHEDULED}")
    assert resp.json()["factories"] == 1
    assert resp.json()["cities"]["臺北市"]["factories"] == 1

    resp = client.get(f"/api/statistics/factories?townname=台北市&display_status={DocumentDisplayStatusConst.AUDIT_SCHEDULED}&source=U")
    assert resp.json()["factories"] == 1
    assert resp.json()["cities"]["臺北市"]["factories"] == 1

    resp = client.get(f"/api/statistics/factories?townname=台北市&display_status={DocumentDisplayStatusConst.AUDIT_SCHEDULED}&source=G")
    assert resp.json()["factories"] == 0
    assert resp.json()["cities"]["臺北市"]["factories"] == 0

    # Add 3 documents to factories in 臺北市中山區
    Document.objects.create(
        cet_staff="AAA",
        code="123457",
        factory=Factory.objects.get(id=id_list[0]),
        display_status=DocumentDisplayStatusEnum.INDICES[DocumentDisplayStatusConst.AUDIT_SCHEDULED]
    )
    Document.objects.create(
        cet_staff="AAA",
        code="123457",
        factory=Factory.objects.get(id=id_list[1]),
        display_status=DocumentDisplayStatusEnum.INDICES[DocumentDisplayStatusConst.COMMUNICATION_PERIOD]
    )
    Document.objects.create(
        cet_staff="AAA",
        code="123457",
        factory=Factory.objects.get(id=id_list[2]),
        display_status=DocumentDisplayStatusEnum.INDICES[DocumentDisplayStatusConst.WORK_STOPPED]
    )

    resp = client.get("/api/statistics/factories?townname=台北市")
    assert resp.json()["documents"] == 5
    assert resp.json()["cities"]["臺北市"]["documents"] == 5

    resp = client.get(f"/api/statistics/factories?townname=台北市&display_status={DocumentDisplayStatusConst.IN_PROGRESS}")
    assert resp.json()["documents"] == 3
    assert resp.json()["cities"]["臺北市"]["documents"] == 3

    Document.objects.create(
        cet_staff="AAA",
        code="123457",
        factory=Factory.objects.get(id=id_list[3]),
        display_status=DocumentDisplayStatusEnum.INDICES[DocumentDisplayStatusConst.REPORTED]
    )
    Document.objects.create(
        cet_staff="AAA",
        code="123457",
        factory=Factory.objects.get(id=id_list[3]),
        display_status=DocumentDisplayStatusEnum.INDICES[DocumentDisplayStatusConst.DEMOLITION_SCHEDULED]
    )

    resp = client.get(f"/api/statistics/factories?townname=台北市&display_status={DocumentDisplayStatusConst.IN_PROGRESS}")
    assert resp.json()["documents"] == 4


def test_get_image_statistics(client):
    for _ in range(10):
        create_factory(client)

    resp = client.get("/api/statistics/images?townname=台北市")
    assert resp.json()["count"] == 20, f"expect 20 but {resp.json()['count']}"

    resp = client.get("/api/statistics/images")
    assert resp.json()["count"] == 20, f"expect 20 but {resp.json()['count']}"

    resp = client.get("/api/statistics/images?townname=台南市")
    assert resp.json()["count"] == 0, f"expect 0 but {resp.json()['count']}"

    resp = client.get("/api/statistics/images?townname=台北市大同區")
    assert resp.json()["count"] == 0, f"expect 0 but {resp.json()['count']}"


def test_get_report_records_statistics(client):
    for _ in range(10):
        create_factory(client)

    resp = client.get("/api/statistics/report_records?townname=台北市")
    assert resp.json()["count"] == 10, f"expect 10 but {resp.json()['count']}"

    resp = client.get("/api/statistics/report_records")
    assert resp.json()["count"] == 10, f"expect 10 but {resp.json()['count']}"

    resp = client.get("/api/statistics/report_records?townname=台南市")
    assert resp.json()["count"] == 0, f"expect 0 but {resp.json()['count']}"

    resp = client.get("/api/statistics/report_records?townname=台北市大同區")
    assert resp.json()["count"] == 0, f"expect 0 but {resp.json()['count']}"


def test_get_total(client):
    id_list = [
        create_factory(client)
        for _ in range(10)
    ]

    for factory_id in id_list:
        Document.objects.create(
            cet_staff="AAA",
            code="123456",
            factory=Factory.objects.get(id=factory_id),
            display_status=0
        )

    resp = client.get("/api/statistics/total")
    assert resp.json()["臺北市"]["documents"] == 10
    count = resp.json()["臺北市"][DocumentDisplayStatusConst.OPEN]
    assert count == 10, f"expect 10 but {count}"

    for factory in Factory.objects.order_by("-created_at").all()[:5]:
        Document.objects.create(
            cet_staff="AAA",
            code="123456",
            factory=factory,
            display_status=1
        )

    resp = client.get("/api/statistics/total")
    assert resp.json()["臺南市"]["documents"] == 5
    count = resp.json()["臺南市"][DocumentDisplayStatusConst.IN_PROGRESS]
    assert count == 5, f"expect 5 but {count}"

    for factory in Factory.objects.order_by("-created_at").all()[5:10]:
        Document.objects.create(
            cet_staff="AAA",
            code="123456",
            factory=factory,
            display_status=2
        )

    resp = client.get("/api/statistics/total")
    assert resp.json()["臺南市"]["documents"] == 10
    count = resp.json()["臺南市"][DocumentDisplayStatusConst.IN_PROGRESS]
    assert count == 10, f"expect 10 but {count}"

    for factory in Factory.objects.order_by("-created_at"):
        Document.objects.create(
            cet_staff="AAA",
            code="123456",
            factory=factory,
            display_status=3
        )

    resp = client.get("/api/statistics/total")
    assert resp.json()["臺南市"]["documents"] == 101
    count = resp.json()["臺南市"][DocumentDisplayStatusConst.IN_PROGRESS]
    assert count == 101, f"expect 101 but {count}"

    count = resp.json()["臺北市"][DocumentDisplayStatusConst.IN_PROGRESS]
    assert count == 10, f"expect 10 but {count}"
