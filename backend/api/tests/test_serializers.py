from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from conftest import SuperSet, Unordered

from ..serializers import FactorySerializer, ImageSerializer
from ..models import Factory, ReportRecord, Image


@pytest.mark.django_db
class TestFactorySerializers:

    @pytest.fixture
    def images(self, db):
        return [
            Image.objects.create(image_path="https://i.imgur.com/RxArJUc.png"),
            Image.objects.create(image_path="https://imgur.dcard.tw/BB2L2LT.jpg"),
        ]

    @pytest.fixture
    def request_body(self, images):
        return {
            "name": "a new factory",
            "type": "2-3",
            "images": [image.id for image in images],
            "other": "這個工廠實在太臭啦，趕緊檢舉吧",
            "lat": 23.234,
            "lng": 120.1,
            "nickname": "路過的家庭主婦",
            "contact": "07-7533967",
        }

    def test_factory_serializer_correct_report_date(self):
        factory = Factory(
            name="test factory",
            lat=23,
            lng=121,
            landcode="000120324",
            factory_type="2-1",
            cet_report_status="A",
            status_time=datetime.now(),
            display_number=666,
        )
        factory.save()

        # created first time, w/o any ReportRecord
        # should have null reported_at
        serialized_factory = FactorySerializer(factory)
        assert serialized_factory.data == SuperSet({
            'type': factory.factory_type,
            'display_number': factory.display_number,
            'reported_at': None,
        })

        report_record1 = ReportRecord.objects.create(
            factory=factory,
            action_type="post_image",
            action_body={},
            contact="0800-092000",
            others="猴～被我拍到了吧",
            created_at=factory.created_at + timedelta(seconds=1),
        )
        im1 = Image.objects.create(
            image_path="https://i.imgur.com/RxArJUc.png",
            deletehash="qwerasdfzxcv;",
            factory=factory,
            report_record=report_record1,
        )
        report_record2 = ReportRecord.objects.create(
            factory=factory,
            action_type="post_image",
            action_body={},
            contact="07-7533967",
            others="昨天在這裡辦演唱會，但旁邊居然在蓋工廠。不錄了不錄了！",
            created_at=factory.created_at + timedelta(days=1),
        )
        im2 = Image.objects.create(
            image_path="https://imgur.dcard.tw/BB2L2LT.jpg",
            factory=factory,
            report_record=report_record2,
            deletehash="qwerasdfzxcv;",
        )
        report_record_latest = ReportRecord.objects.create(
            factory=factory,
            action_type="PUT",
            action_body={"status": "D"},
            contact="02-2392-0371",
            others="已呈報",
            created_at=factory.created_at + timedelta(days=2),
        )  # this one should be the `reported_at` of serialized factory
        factory.refresh_from_db()
        serialized_factory = FactorySerializer(factory)
        assert serialized_factory.data == SuperSet({
            'reported_at': report_record_latest.created_at,
            'images': Unordered([
                ImageSerializer(im1).data,
                ImageSerializer(im2).data,
            ]),
        })

    def test_factory_serializer_validate_body(self, request_body):
        serializer = FactorySerializer(data=request_body)
        assert serializer.is_valid()

    def test_factory_serializer_validate_body_with_wrong_lat(self, request_body):
        wrong_request_body = {
            **request_body,
            "lat": 70,
        }
        serializer = FactorySerializer(data=wrong_request_body)

        assert not serializer.is_valid()
        assert "lat" in serializer.errors

    def test_factory_serializer_validate_body_with_wrong_lng(self, request_body):
        wrong_request_body = {
            **request_body,
            "lng": -10,
        }
        serializer = FactorySerializer(data=wrong_request_body)

        assert not serializer.is_valid()
        assert "lng" in serializer.errors

    def test_data_complete_false_if_no_type_for_old(self):
        factory = Factory.objects.create(
            name="test factory",
            lat=23,
            lng=121,
            landcode="000120324",
            factory_type=None,
            before_release=True,
            cet_report_status="A",
            status_time=datetime.now(),
            display_number=666,
        )
        report_record2 = ReportRecord.objects.create(
            factory=factory,
            action_type="post_image",
            action_body={},
            contact="07-7533967",
            others="昨天在這裡辦演唱會，但旁邊居然在蓋工廠。不錄了不錄了！",
            created_at=factory.created_at + timedelta(days=1),
        )
        Image.objects.create(
            image_path="https://imgur.dcard.tw/BB2L2LT.jpg",
            factory=factory,
            report_record=report_record2,
            deletehash="qwerasdfzxcv;"
        )
        serializer = FactorySerializer(factory)
        assert not serializer.data["data_complete"]

    def test_data_complete_false_if_no_image_for_old(self):
        factory = Factory.objects.create(
            name="test factory",
            lat=23,
            lng=121,
            landcode="000120324",
            factory_type=None,
            before_release=True,
            cet_report_status="A",
            created_at=datetime.now() - timedelta(days=100),
            status_time=datetime.now(),
            display_number=666,
        )
        ReportRecord.objects.create(
            factory=factory,
            action_type="HI",
            action_body={},
            contact="07-7533967",
            others="HI",
            created_at=factory.created_at + timedelta(days=1),
        )
        serializer = FactorySerializer(factory)
        assert not serializer.data["data_complete"]

    def test_data_complete_false_if_last_report_longer_than_one_year_ago(self):
        test_time = datetime.now() - timedelta(days=365 * 2)
        with freeze_time(test_time):
            factory = Factory.objects.create(
                name="test factory",
                lat=23,
                lng=121,
                landcode="000120324",
                factory_type="8",
                before_release=True,
                cet_report_status="A",
                display_number=666,
            )
            report_record = ReportRecord.objects.create(
                factory=factory,
                action_type="post_image",
                action_body={},
                contact="07-7533967",
                others="昨天在這裡辦演唱會，但旁邊居然在蓋工廠。不錄了不錄了！",
                created_at=factory.created_at + timedelta(days=1),
            )
            Image.objects.create(
                image_path="https://imgur.dcard.tw/BB2L2LT.jpg",
                factory=factory,
                deletehash="qwerasdfzxcv;",
                report_record=report_record,
            )
        serializer = FactorySerializer(factory)
        assert not serializer.data["data_complete"]

    def test_data_complete_true(self):
        factory_create = datetime.now() - timedelta(days=365)
        with freeze_time(factory_create):
            factory = Factory.objects.create(
                name="test factory",
                lat=23,
                lng=121,
                landcode="000120324",
                factory_type="8",
                before_release=True,
                cet_report_status="A",
                display_number=666,
            )
        report_time = datetime.now() - timedelta(days=364)
        with freeze_time(report_time):
            report_record = ReportRecord.objects.create(
                factory=factory,
                action_type="post_image",
                action_body={},
                contact="07-7533967",
                others="昨天在這裡辦演唱會，但旁邊居然在蓋工廠。不錄了不錄了！",
            )
            Image.objects.create(
                image_path="https://imgur.dcard.tw/BB2L2LT.jpg",
                factory=factory,
                deletehash="qwerasdfzxcv;",
                report_record=report_record,
            )
        serializer = FactorySerializer(factory)
        assert serializer.data["data_complete"]

    def test_data_complete_true_after_2016(self):
        factory_create = datetime.now() - timedelta(days=365)
        with freeze_time(factory_create):
            factory = Factory.objects.create(
                name="test factory",
                lat=23,
                lng=121,
                landcode="000120324",
                factory_type="8",
                before_release=False,
                cet_report_status="A",
                display_number=666,
            )
        report_time = datetime.now() - timedelta(days=364)
        with freeze_time(report_time):
            report_record = ReportRecord.objects.create(
                factory=factory,
                action_type="post_image",
                action_body={},
                contact="07-7533967",
                others="昨天在這裡辦演唱會，但旁邊居然在蓋工廠。不錄了不錄了！",
            )
            Image.objects.create(
                image_path="https://imgur.dcard.tw/BB2L2LT.jpg",
                factory=factory,
                report_record=report_record,
                deletehash="qwerasdfzxcv;",
            )
        serializer = FactorySerializer(factory)
        assert serializer.data["data_complete"]

    def test_data_complete_true_after_2016_no_image(self):
        factory_create = datetime.now() - timedelta(days=365)
        with freeze_time(factory_create):
            factory = Factory.objects.create(
                name="test factory",
                lat=23,
                lng=121,
                landcode="000120324",
                factory_type="8",
                before_release=False,
                cet_report_status="A",
                display_number=666,
            )
        report_time = datetime.now() - timedelta(days=364)
        with freeze_time(report_time):
            ReportRecord.objects.create(
                factory=factory,
                action_type="post_image",
                action_body={},
                contact="07-7533967",
                others="昨天在這裡辦演唱會，但旁邊居然在蓋工廠。不錄了不錄了！",
            )
        serializer = FactorySerializer(factory)
        assert not serializer.data["data_complete"]

    def test_data_complete_false_after_long_time_no_report(self):
        factory_create = datetime.now() - timedelta(days=365 * 2)
        with freeze_time(factory_create):
            factory = Factory.objects.create(
                name="test factory",
                lat=23,
                lng=121,
                landcode="000120324",
                factory_type="8",
                before_release=False,
                cet_report_status="A",
                display_number=666,
            )
        report_time = datetime.now() - timedelta(days=366)
        with freeze_time(report_time):
            report_record = ReportRecord.objects.create(
                factory=factory,
                action_type="post_image",
                action_body={},
                contact="07-7533967",
                others="昨天在這裡辦演唱會，但旁邊居然在蓋工廠。不錄了不錄了！",
            )
            Image.objects.create(
                image_path="https://imgur.dcard.tw/BB2L2LT.jpg",
                factory=factory,
                report_record=report_record,
                deletehash="qwerasdfzxcv;",
            )
        serializer = FactorySerializer(factory)
        assert not serializer.data["data_complete"]

    def test_allow_empty_factory_type(self, request_body):
        request_body.pop('type')
        serializer = FactorySerializer(data=request_body)

        assert serializer.is_valid()

    def test_allow_None_factory_type(self, request_body):
        request_body['type'] = None
        serializer = FactorySerializer(data=request_body)

        assert serializer.is_valid()


def test_image_serializer_coorect_url():
    img = Image(image_path="https://imgur.com/qwer")
    serialized_img = ImageSerializer(img)

    assert serialized_img.data["url"] == img.image_path
    assert serialized_img.data.get("deletehash") is None
