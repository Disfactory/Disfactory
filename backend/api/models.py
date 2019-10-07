# -*- coding: utf-8 -*-
from django.contrib.gis.db import models
from django.conf import settings

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
    id =  models.UUIDField(max_length=36, primary_key=True, serialize=False, verbose_name='ID')
    fact_name = models.CharField(max_length=50, blank=True, null=True)
    lat = models.FloatField(max_length=16)
    lng = models.FloatField(max_length=16)
    landcode = models.CharField (max_length=50, blank=True, null=True)
    fact_type = models.CharField(max_length=1, choices=fact_type_list)
    status = models.CharField(max_length=1, choices=status_list)
    status_time = models.DateField()
    others = models.CharField(max_length=1024, blank=True)
    creat_at = models.DateTimeField(auto_now_add=True)

    # % Discussion!!
    # fact_no = models.AutoField(max_length=36, unique=True, serialize=True, verbose_name='Factory No.')     Readable id (unique)
    # update_time =  models.DateField(auto_now=True)   The last time of the change

    # TODO: write a migration for data initialization, ref: https://docs.djangoproject.com/en/2.2/howto/initial-data/ 
      # % I still have no idea about this step. I have to make a example by myself without using the command "makemigration" because the DB is not ready?
    
    point = models.PointField(srid=settings.POSTGIS_SRID)


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
    id = models.ForeignKey('Factory', on_delete=models.PROTECT)
    user_ip = models.GenericIPAddressField(default='192.168.0.1', blank=True, null=True)
    action_type = models.CharField(max_length=10)
    action_body = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    contect = models.CharField(max_length=64, blank=True, null=True)
    pass


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
    id = models.ForeignKey('Factory', on_delete=models.PROTECT)
    image_id = models.CharField(max_length=128)
    image_path = models.URLField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    orig_time = models.DateTimeField(blank=True, null=True)
    pass
