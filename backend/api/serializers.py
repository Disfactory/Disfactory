from datetime import timedelta

from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    SerializerMethodField,
)
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Factory, Image, ReportRecord, Document


VALID_FACTORY_TYPES = [t[0] for t in Factory.factory_type_list]


class ImageSerializer(ModelSerializer):

    url = CharField(source="image_path")

    class Meta:
        model = Image
        fields = ["id", "image_path", "url"]


class FactorySerializer(ModelSerializer):

    images = ImageSerializer(many=True, read_only=True)
    type = CharField(source="factory_type", required=False, allow_null=True)
    reported_at = SerializerMethodField()
    data_complete = SerializerMethodField()
    status = SerializerMethodField()  # should be DEPRECATED
    document_display_status = SerializerMethodField()

    class Meta:
        model = Factory
        fields = [
            "id",
            "display_number",
            "lat",
            "lng",
            "name",
            "landcode",
            "factory_type",
            "type",
            "cet_report_status",
            "before_release",
            "images",
            "reported_at",
            "data_complete",
            "status",  # should be DEPRECATED
            "document_display_status",
        ]
        extra_kwargs = {
            "display_number": {"required": False},
        }

    def get_status(self, obj):
        return obj.cet_report_status

    def get_reported_at(self, obj):
        report_records = ReportRecord.objects.only("created_at").filter(factory=obj)
        if len(report_records) == 0:
            return None
        reported_date = [record.created_at for record in report_records]
        return sorted(reported_date, reverse=True)[0]

    def get_data_complete(self, obj):
        images = Image.objects.only("id").filter(factory=obj)
        report_records = (
            ReportRecord.objects.only("created_at")
            .filter(factory=obj)
            .order_by("-created_at")
        )
        has_type = obj.factory_type is not None
        has_photo = len(images) > 0
        if report_records:
            last_year = timezone.now() - timedelta(days=365)
            reported_within_1_year = report_records[0].created_at > last_year
        else:  # don't have any report records
            reported_within_1_year = False

        if obj.before_release:
            return has_photo and reported_within_1_year and has_type
        else:
            return has_photo and reported_within_1_year

    def get_document_display_status(self, obj):
        latestDocument = Document.objects.only("display_status").filter(factory=obj).order_by("-created_at")

        if len(latestDocument) == 0:
            return None
        else:
            return latestDocument[0].get_display_status_display()

    def validate_lat(self, value):
        if value < settings.TAIWAN_MIN_LATITUDE or value > settings.TAIWAN_MAX_LATITUDE:
            raise ValidationError(
                f"latitude should be within {settings.TAIWAN_MIN_LATITUDE} "
                f"~ {settings.TAIWAN_MAX_LATITUDE}, but got {value}"
            )

    def validate_lng(self, value):
        if (
            value < settings.TAIWAN_MIN_LONGITUDE
            or value > settings.TAIWAN_MAX_LONGITUDE
        ):
            raise ValidationError(
                f"longitude should be within {settings.TAIWAN_MIN_LONGITUDE} "
                f"~ {settings.TAIWAN_MAX_LONGITUDE}, but got {value}"
            )

    def validate_type(self, value):
        if (value is not None) and (value not in VALID_FACTORY_TYPES):
            raise ValidationError(
                'Factory Type "{}" is not one of the permitted values: {}'.format(
                    value, ", ".join(VALID_FACTORY_TYPES)
                )
            )


class ReportRecordSerializer(ModelSerializer):

    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = ReportRecord
        fields = [
            "id",
            "factory",
            "user_ip",
            "action_type",
            "action_body",
            "created_at",
            "nickname",
            "contact",
            "others",
            "images",
        ]
