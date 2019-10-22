# -*- coding: utf-8 -*-
import uuid

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import JSONField


class Factory(models.Model):
    """Factories that are potential to be illegal."""

    # List of fact_type & status
    factory_type_list = [
        ("1","金屬"),
        ("2-1","沖床、銑床、車床、鏜孔"),
        ("2-2", "焊接、鑄造、熱處理"),
        ("2-3", "金屬表面處理、噴漆"),
        ("3", "塑膠加工、射出"),
        ("4", "橡膠加工"),
        ("5", "非金屬礦物（石材）"),
        ("6", "食品"),
        ("7", "皮革"),
        ("8", "紡織"),
        ("9", "其他")
    ]
    status_list = [
        ("D","已舉報"),
        ("F","資料不齊"),
        ("A","待審核")
    ]

    # All  Features
    id =  models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )

    lat = models.FloatField()
    lng = models.FloatField()
    point = models.PointField(srid=settings.POSTGIS_SRID)
    landcode = models.CharField(max_length=50, blank=True, null=True)

    name = models.CharField(max_length=50, blank=True, null=True)
    factory_type = models.CharField(max_length=3, choices=factory_type_list, default="9")
    status = models.CharField(max_length=1, choices=status_list)
    status_time = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.point = Point(self.lng, self.lat, srid=4326)
        self.point.transform(settings.POSTGIS_SRID)
        super(Factory, self).save(*args, **kwargs)


class ReportRecord(models.Model):
    """Report records send by users.

    `ReportRecord` will be queried in advanced by admins from
    Citizen of the Earth, Taiwan. They will filter the most recent
    records out every a few weeks to catch the bad guys.
    """

    id = models.AutoField(primary_key=True)
    factory = models.ForeignKey("Factory", on_delete=models.PROTECT)
    user_ip = models.GenericIPAddressField(default="192.168.0.1", blank=True, null=True)
    action_type = models.CharField(max_length=10)  # PUT, POST
    action_body = JSONField()  # request body
    created_at = models.DateTimeField(auto_now_add=True)
    contact = models.CharField(max_length=64, blank=True, null=True)
    others = models.CharField(max_length=1024, blank=True)


class Image(models.Model):
    """Images of factories that are uploaded by user."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    factory = models.ForeignKey(
        "Factory",
        on_delete=models.PROTECT,
        related_name="images",
    )
    report_record = models.ForeignKey(
        "ReportRecord",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    image_path = models.URLField(max_length=256)  # get from Imgur
    created_at = models.DateTimeField(auto_now_add=True)
    # the DB saving time

    orig_time = models.DateTimeField(blank=True, null=True)
    # the actual photo taken time
