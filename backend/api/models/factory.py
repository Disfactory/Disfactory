import uuid

from django.db import models
from django.contrib.auth import get_user_model

from .mixins import SoftDeleteMixin

CustomUser = get_user_model()


class Factory(SoftDeleteMixin):
    """Factories that are potential to be illegal."""

    # List of fact_type & status
    factory_type_list = [
        ("2-1", "沖床、銑床、車床、鏜孔"),
        ("2-2", "焊接、鑄造、熱處理"),
        ("2-3", "金屬表面處理、噴漆"),
        ("3", "塑膠加工、射出"),
        ("4", "橡膠加工"),
        ("5", "非金屬礦物（石材）"),
        ("6", "食品"),
        ("7", "皮革"),
        ("8", "紡織"),
        ("9", "其他"),
    ]
    cet_review_status_list = [
        ("A", "尚未審查"),
        ("O", "已審查-不檢舉"),
        ("P", "已審查-需補件"),
        ("Q", "已審查-待檢舉"),
        ("X", "已審查-已生成公文"),
    ]
    cet_report_status_list = [
        ("A", "未舉報"),
        ("O", "第一次發文待回覆"),
        ("P", "第一次發文已播電話追蹤"),
        ("Q", "第一次回文"),
        ("X", "第二次發文待回覆"),
        ("Y", "第二次發文已播電話追蹤"),
        ("Z", "第二次回文"),
        ("B", "已結案"),
    ]
    source_list = [
        ("G", "政府"),
        ("U", "使用者"),
    ]

    # All Features
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    display_number = models.IntegerField(unique=True)

    lat = models.FloatField()
    lng = models.FloatField()
    landcode = models.CharField(max_length=50, blank=True, null=True)
    towncode = models.CharField(max_length=50, blank=True, null=True)
    townname = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    sectcode = models.CharField(max_length=50, blank=True, null=True)
    sectname = models.CharField(max_length=50, blank=True, null=True)

    name = models.CharField(max_length=50, blank=True, null=True)
    factory_type = models.CharField(
        max_length=3,
        choices=factory_type_list,
        blank=True,
        null=True,
    )
    before_release = models.BooleanField(
        default=False
    )  # 從 full-info.csv 匯入的那些都是 True ，使用者新增的通通是 False
    source = models.CharField(
        max_length=1,
        choices=source_list,
        default="U",
    )
    cet_review_status = models.CharField(
        max_length=1,
        choices=cet_review_status_list,
        default="A",
    )  # 地球公民基金會的審閱狀態（舉報前）
    cet_report_status = models.CharField(
        max_length=1,
        choices=cet_report_status_list,
        default="A",
    )  # 地球公民基金會的舉報狀態

    cet_reviewer = models.ForeignKey(
        to=CustomUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )  # 審查人

    status_time = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RecycledFactory(Factory):
    class Meta:
        proxy = True

    objects = Factory.recycle_objects
