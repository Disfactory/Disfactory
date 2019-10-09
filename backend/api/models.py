# -*- coding: utf-8 -*-
import uuid

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField


class Factory(models.Model):
    """Factories that are potential to be illegal.
            Containing:
           - id :  Safety concern (primary key)
           - fact_name
           - lat
           - lng
           - landcode
           - fact_type
           - status :  The status of the processes
           - status_time :  The last time of updating the status
           - others :  Attachment of the description
           - creat_at
       """

    # List of fact_type & status
    fact_type_list = [
        ('1','金屬'),
        ('2-1','沖床、銑床、車床、鏜孔'),
        ('2-2', '焊接、鑄造、熱處理'),
        ('2-3', '金屬表面處理、噴漆'),
        ('3', '塑膠加工、射出'),
        ('4', '橡膠加工'),
        ('5', '非金屬礦物（石材）'),
        ('6', '食品'),
        ('7', '皮革'),
        ('8', '紡織'),
        ('9', '其他')
    ]
    status_list = [
        ('D','已舉報'),
        ('F','資料不齊'),
        ('A','待審核')
    ]

    # All  Features
    id =  models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID',
    )

    lat = models.FloatField()
    lng = models.FloatField()
    point = models.PointField(srid=settings.POSTGIS_SRID)
    landcode = models.CharField (max_length=50, blank=True, null=True)

    name = models.CharField(max_length=50, blank=True, null=True)
    factory_type = models.CharField(max_length=3, choices=fact_type_list, default='9')
    status = models.CharField(max_length=1, choices=status_list)
    status_time = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO: write a migration for data initialization, ref: https://docs.djangoproject.com/en/2.2/howto/initial-data/


class ReportRecord(models.Model):
    """Report records send by users.
        `ReportRecord` will be queried in advanced by admins from
        Citizen of the Earth, Taiwan. They will filter the most recent
        records out every a few weeks to catch the bad guys.
        Containing:
        - id : Foreign Key related to "Factory"
        - user_ip
        - action_type :  (e.g. PUT)
        - action_body :  The request
        - created_at
        - contect :  Could be emall, phone number, nick name and so on
       """
    id = models.AutoField(primary_key=True)
    factory = models.ForeignKey('Factory', on_delete=models.PROTECT)
    user_ip = models.GenericIPAddressField(default='192.168.0.1', blank=True, null=True)
    action_type = models.CharField(max_length=10)
    action_body = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    contact = models.CharField(max_length=64, blank=True, null=True)
    others = models.CharField(max_length=1024, blank=True)


class Image(models.Model):
    """Images of factories that are uploaded by user
        We store the actual image files on Imgur, so this table
        should contain :
        - id :  Foreign Key related to "Factory"
        - image_id
        - image_path
        - created_at :  Uploading time
        - orig_time :  The time of taking the picture
        """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    factory = models.ForeignKey('Factory', on_delete=models.PROTECT)
    report_record = models.ForeignKey(
        'ReportRecord',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    image_path = models.URLField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    orig_time = models.DateTimeField(blank=True, null=True)
    pass
