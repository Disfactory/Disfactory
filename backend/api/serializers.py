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
        return max(record.created_at for record in report_records)

    def get_data_complete(self, obj):
        # has_photo and reported_within_1_year and (not before_release or has_type)
        if len(Image.objects.only("id").filter(factory=obj)) == 0:
            return False  # no photo
        latest_record = ReportRecord.objects.only("created_at").filter(
            factory=obj).latest('created_at')
        if not (
            latest_record
            and latest_record.created_at > timezone.now() - timedelta(days=365)
        ):
            return False  # not reported or outdated

        if obj.before_release:
            return obj.factory_type is not None
        else:
            return True

    def get_document_display_status(self, obj):
        latestDocument = Document.objects.only("display_status").filter(factory=obj).order_by("-created_at")

        if len(latestDocument) == 0:
            return None
        else:
            return latestDocument[0].get_display_status_display()

    def validate_lat(self, value):
        if not (settings.TAIWAN_MIN_LATITUDE <= value <= settings.TAIWAN_MAX_LATITUDE):
            raise ValidationError(
                f"latitude should be within {settings.TAIWAN_MIN_LATITUDE} "
                f"~ {settings.TAIWAN_MAX_LATITUDE}, but got {value}"
            )

    def validate_lng(self, value):
        if not (settings.TAIWAN_MIN_LONGITUDE <= value <= settings.TAIWAN_MAX_LONGITUDE):
            raise ValidationError(
                f"longitude should be within {settings.TAIWAN_MIN_LONGITUDE} "
                f"~ {settings.TAIWAN_MAX_LONGITUDE}, but got {value}"
            )

    def validate_type(self, value):
        if (value is not None) and (value not in VALID_FACTORY_TYPES):
            valid_type_msg = ", ".join(VALID_FACTORY_TYPES)
            raise ValidationError(
                f'Factory Type "{value}" is not one of the permitted values: {valid_type_msg}',
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
