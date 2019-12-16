from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    SerializerMethodField,
    ValidationError,
)

from .models import Factory, Image, ReportRecord
from django.conf import settings


class ImageSerializer(ModelSerializer):

    url = CharField(source="image_path")

    class Meta:
        model = Image
        fields = ["id", "image_path", "url"]


class FactorySerializer(ModelSerializer):

    images = ImageSerializer(many=True, read_only=True)
    type = CharField(source="factory_type")
    reported_at = SerializerMethodField()

    class Meta:
        model = Factory
        fields = [
            "id",
            "lat",
            "lng",
            "name",
            "landcode",
            "factory_type",
            "type",
            "status",
            "images",
            "reported_at",
        ]

    def get_reported_at(self, obj):
        report_records = ReportRecord.objects.only("created_at").filter(factory=obj)
        if len(report_records) == 0:
            return None
        reported_date = [record.created_at for record in report_records]
        return sorted(reported_date, reverse=True)[0]

    def validate_lat(self, value):
        if value < TAIWAN_MIN_LATITUDE or value > TAIWAN_MAX_LATITUDE:
            raise ValidationError(f"latitude should be within 22 ~ 25, but got {value}")

    def validate_lng(self, value):
        if value < TAIWAN_MIN_LONGITUDE or value > TAIWAN_MAX_LONGITUDE:
            raise ValidationError(f"longitude should be within 120 ~ 122, but got {value}")

