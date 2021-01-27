import datetime

from django.test import TestCase, Client
from freezegun import freeze_time

from ...models import Image, Factory, Document, ReportRecord


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


class GetStatisticsTestCase(TestCase):
    def setUp(self):
        self.cli = Client()

    def test_get_factory_statistics(self):
        cli = Client()

        id_list = []
        for index in range(0, 10):
            result = create_factory(cli)
            id_list.append(result)

        resp = self.cli.get("/api/statistics/factories?source=U")
        assert resp.json()["count"] == 10

        resp = self.cli.get("/api/statistics/factories?townname=台北市")
        assert resp.json()["count"] == 10

        resp = self.cli.get("/api/statistics/factories?townname=台北市中山區")
        assert resp.json()["count"] == 10

        resp = self.cli.get("/api/statistics/factories?townname=台南市")
        assert resp.json()["count"] == 101

        resp = self.cli.get("/api/statistics/factories?display_status=已檢舉")
        assert resp.json()["count"] == 0

        Document.objects.create(
            cet_staff="AAA",
            code="123456",
            factory=Factory.objects.get(id=id_list[0]),
            display_status=0
        )

        resp = self.cli.get("/api/statistics/factories?display_status=已檢舉")
        assert resp.json()["count"] == 1, f"expect 1 but {resp.json()['count']}"

        resp = self.cli.get("/api/statistics/factories?townname=台南市&display_status=已檢舉")
        assert resp.json()["count"] == 0, f"expect 0 but {resp.json()['count']}"

        resp = self.cli.get("/api/statistics/factories?townname=台北市&display_status=已檢舉")
        assert resp.json()["count"] == 1, f"expect 1 but {resp.json()['count']}"

        Document.objects.create(
            cet_staff="AAA",
            code="123457",
            factory=Factory.objects.get(id=id_list[0]),
            display_status=1
        )
        resp = self.cli.get("/api/statistics/factories?townname=台北市&display_status=已檢舉")
        assert resp.json()["count"] == 0, f"expect 0 but {resp.json()['count']}"

        resp = self.cli.get("/api/statistics/factories?townname=台北市&display_status=已排程稽查")
        assert resp.json()["count"] == 1, f"expect 1 but {resp.json()['count']}"

        resp = self.cli.get("/api/statistics/factories?townname=台北市&display_status=已排程稽查&source=U")
        assert resp.json()["count"] == 1, f"expect 1 but {resp.json()['count']}"

        resp = self.cli.get("/api/statistics/factories?townname=台北市&display_status=已排程稽查&source=G")
        assert resp.json()["count"] == 0, f"expect 0 but {resp.json()['count']}"

        Document.objects.create(
            cet_staff="AAA",
            code="123457",
            factory=Factory.objects.get(id=id_list[0]),
            display_status=2
        )
        Document.objects.create(
            cet_staff="AAA",
            code="123457",
            factory=Factory.objects.get(id=id_list[1]),
            display_status=2
        )
        Document.objects.create(
            cet_staff="AAA",
            code="123457",
            factory=Factory.objects.get(id=id_list[2]),
            display_status=2
        )

        resp = self.cli.get("/api/statistics/factories?townname=台北市&display_status=處理中")
        assert resp.json()["count"] == 3, f"expect 3 but {resp.json()['count']}"

        Document.objects.create(
            cet_staff="AAA",
            code="123457",
            factory=Factory.objects.get(id=id_list[3]),
            display_status=0
        )
        Document.objects.create(
            cet_staff="AAA",
            code="123457",
            factory=Factory.objects.get(id=id_list[3]),
            display_status=1
        )

        resp = self.cli.get("/api/statistics/factories?townname=台北市&display_status=處理中")
        assert resp.json()["count"] == 4, f"expect 4 but {resp.json()['count']}"


    def test_get_image_statistics(self):
        cli = Client()
        id_list = []
        for index in range(0, 10):
            result = create_factory(cli)
            id_list.append(result)

        resp = self.cli.get("/api/statistics/images?townname=台北市")
        assert resp.json()["count"] == 20, f"expect 20 but {resp.json()['count']}"

        resp = self.cli.get("/api/statistics/images")
        assert resp.json()["count"] == 20, f"expect 20 but {resp.json()['count']}"

        resp = self.cli.get("/api/statistics/images?townname=台南市")
        assert resp.json()["count"] == 0, f"expect 0 but {resp.json()['count']}"

        resp = self.cli.get("/api/statistics/images?townname=台北市大同區")
        assert resp.json()["count"] == 0, f"expect 0 but {resp.json()['count']}"

    def test_get_report_records_statistics(self):
        cli = Client()
        id_list = []
        for index in range(0, 10):
            result = create_factory(cli)
            id_list.append(result)

        resp = self.cli.get("/api/statistics/report_records?townname=台北市")
        assert resp.json()["count"] == 10, f"expect 10 but {resp.json()['count']}"

        resp = self.cli.get("/api/statistics/report_records")
        assert resp.json()["count"] == 10, f"expect 10 but {resp.json()['count']}"

        resp = self.cli.get("/api/statistics/report_records?townname=台南市")
        assert resp.json()["count"] == 0, f"expect 0 but {resp.json()['count']}"

        resp = self.cli.get("/api/statistics/report_records?townname=台北市大同區")
        assert resp.json()["count"] == 0, f"expect 0 but {resp.json()['count']}"

    def test_get_total(self):
        cli = Client()
        id_list = []
        for index in range(0, 10):
            result = create_factory(cli)
            id_list.append(result)

        for factory_id in id_list:
            Document.objects.create(
                cet_staff="AAA",
                code="123456",
                factory=Factory.objects.get(id=factory_id),
                display_status=0
            )

        resp = self.cli.get("/api/statistics/total")
        count = resp.json()["臺北市"]["未處理"]
        assert count == 10, f"expect 10 but {count}"

        for factory in Factory.objects.order_by("-created_at").all()[:5]:
            Document.objects.create(
                cet_staff="AAA",
                code="123456",
                factory=factory,
                display_status=1
            )

        resp = self.cli.get("/api/statistics/total")
        count = resp.json()["臺南市"]["處理中"]
        assert count == 5, f"expect 5 but {count}"

        for factory in Factory.objects.order_by("-created_at").all()[5:10]:
            Document.objects.create(
                cet_staff="AAA",
                code="123456",
                factory=factory,
                display_status=2
            )

        resp = self.cli.get("/api/statistics/total")
        count = resp.json()["臺南市"]["處理中"]
        assert count == 10, f"expect 10 but {count}"

        for factory in Factory.objects.order_by("-created_at"):
            Document.objects.create(
                cet_staff="AAA",
                code="123456",
                factory=factory,
                display_status=3
            )

        resp = self.cli.get("/api/statistics/total")
        count = resp.json()["臺南市"]["處理中"]
        assert count == 101, f"expect 101 but {count}"

        count = resp.json()["臺北市"]["處理中"]
        assert count == 10, f"expect 10 but {count}"
